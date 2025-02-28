from flask import (
    Flask,
    json,
    request,
    render_template,
    send_file,
    url_for,
    redirect,
    session,
)
from model import model
from datetime import datetime, date, timedelta

# from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = "a1V#9R^l6vhGI'Xyms@]ARPJ"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
server_last_update_time = datetime.now()


@app.route("/")
def index():
    classes = model.get_classes()
    return render_template("index.html", classes=classes)


@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if request.method != "POST":
        classes = model.get_classes()
        return render_template("add_student.html", classes=classes)

    full_name: str = request.form["full_name"]
    age = int(request.form["age"])
    gender = request.form["gender"]
    phone_number = request.form["phone_number"]
    classes = request.form.getlist("classes")
    special_requirements = request.form.get("special_requirements", "")

    model.add_student(
        full_name, age, gender, phone_number, classes, special_requirements
    )

    return redirect(url_for("index"))


@app.route("/add_teacher", methods=["GET", "POST"])
def add_teacher():
    if request.method != "POST":
        # Render the form
        return render_template("add_teacher.html")
    teacher_name = request.form["teacher_name"]
    phone_number = request.form["phone_number"]

    # Call the add_teacher function
    model.add_teacher(teacher_name=teacher_name, phone_number=phone_number)

    return redirect(url_for("index"))  # Redirect after adding teacher


def parse_fields(fields):
    field_types = model.get_field_types()
    fields = json.loads(fields)
    for field in fields:
        for t in field_types:
            if int(field["field_type_id"]) == t["field_type_id"]:
                if not t["field_type_defaults"]:
                    field["defaultValues"] = []
        else:
            field["defaultValues"] = json.dumps(field["defaultValues"])
    return fields


@app.route("/add_class", methods=["GET", "POST"])
def add_class():
    field_types = model.get_field_types()
    if request.method != "POST":
        # For GET request: Retrieve available teachers for the form
        teachers = model.get_teachers()
        packages = model.get_packages()
        return render_template(
            "add_class.html",
            teachers=teachers,
            packages=packages,
            field_types=field_types,
        )

    class_name = request.form["class_name"]
    teacher_ids = request.form.getlist("teacher_ids")  # Multiple teachers
    package_id = request.form["package_id"]
    day_of_week = request.form["day_of_week"]
    time_of_day = request.form["time_of_day"]
    fields = parse_fields(request.form["fields"])

    # Call the function to add a class
    model.add_class(
        class_name=class_name,
        teacher_ids=teacher_ids,
        package_id=package_id,
        day_of_week=day_of_week,
        time_of_day=time_of_day,
        fields=fields,
    )

    return redirect(url_for("index"))  # Redirect after adding the class


@app.route("/add_package", methods=["GET", "POST"])
def add_package():
    if request.method != "POST":
        return render_template("add_package.html")

    package_name = request.form["package_name"]
    price = request.form["price"]

    # Call the function to add a package
    model.add_package(
        package_name=package_name,
        price=price,
    )

    return redirect(url_for("index"))  # Redirect after adding the class


@app.route("/assign_students", methods=["GET", "POST"])
def assign_students():
    if request.method != "POST":
        # For GET request: Retrieve available students and classes
        students = model.get_students()

        classes = model.get_classes()

        # Render the form
        return render_template(
            "assign_students.html", students=students, classes=classes
        )

    class_id = request.form["class_id"]
    student_ids = request.form.getlist("student_ids")  # Get multiple selected students

    # Call the function to assign students
    model.assign_students_to_class(class_id=class_id, student_ids=student_ids)

    return redirect(url_for("index"))  # Redirect after adding the class


@app.route("/ajax_server/", methods=["POST", "GET"])
def ajax_server():
    global server_last_update_time
    if request.method == "GET":
        attendance_date = datetime.now() + timedelta(days=7 * 0)
        class_id = request.args.get("class_id")
        student_id = request.args.get("student_id")
        field = request.args.get("field")
        value = request.args.get("value")
        print(attendance_date, class_id, student_id, field, value)
        model.update_attendance_field(
            class_id, student_id, field, value, attendance_date
        )

        server_last_update_time = datetime.now()
        return str(server_last_update_time)


@app.route("/ajax_poll", methods=["POST", "GET"])
def ajax_poll():
    global server_last_update_time
    if request.method == "GET":
        client_last_update_time = datetime.strptime(
            request.args.get("value"), "%d/%m/%Y %H:%M:%S"
        )
        if client_last_update_time > server_last_update_time:
            return []
        attendance_date = datetime.now() + timedelta(days=7 * 0)
        class_id = request.args.get("class_id")
        return model.get_attendance(class_id, attendance_date)


@app.route("/mark_attendance/<int:class_id>", methods=["GET", "POST"])
def mark_attendance(class_id):
    attendance_date = datetime.now()  # + timedelta(days=7 * 0)
    class_data = model.get_class(class_id)
    print(attendance_date, attendance_date.strftime("%A"), class_data["day_of_week"])
    if attendance_date.strftime("%A") != class_data["day_of_week"]:
        return "%s is not running today" % class_data["class_name"]
    if not model.get_class_payments(class_id, attendance_date):
        model.init_payment_month(class_id, attendance_date)
    attendance = model.get_attendance(class_id, attendance_date)
    if not attendance:
        # mark all students as none attendant
        model.init_attendance_day(class_id, attendance_date)
        attendance = model.get_attendance(class_id, attendance_date)

    if request.method != "POST":
        return render_template(
            "mark_attendance.html", attendance=attendance, class_data=class_data
        )

    # note just collect attendance separatly then payments separatly then fields separatly since they have their own ids no need to be bound to student id
    attendance_vals = {}
    payment_vals = {}
    field_vals = {}

    for data in attendance:
        attendance_vals[data["attendance_id"]] = request.form[
            "student_{}".format(data["attendance_id"])
        ]
        payment_vals[data["payment_id"]] = int(
            request.form.get("paid_{}".format(data["payment_id"]), "off") == "on"
        )

        for field in data["fields"]:

            field_values = request.form.getlist(
                "field_{}".format(field["attendance_field_id"])
            )  # Handles checkboxes
            # Convert values to integers if possible
            try:
                field_values = [int(v) for v in field_values]
            except ValueError:
                pass  # Keep them as strings if conversion fails
            field_vals[field["attendance_field_id"]] = field_values

    # model.mark_attendance(class_id, attendance_date, attendance_records)
    return redirect(url_for("index"))  # Redirect after adding the class


from datetime import datetime, timedelta


@app.route("/view_attendance/<int:class_id>")
def view_attendance(class_id):
    # Get the start_date from the query string or default to the current date
    start_date_str = request.args.get("start_date", None)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    else:
        start_date = datetime.today().replace(day=1)  # First day of the current month

    # Calculate the end_date (3 months from start_date)
    end_date = start_date + timedelta(days=30)  # Approx. 3 months

    # Fetch class data and attendance filtered by date range
    class_data = model.get_class(class_id)
    attendance = model.get_class_attendance_in_date_range(
        class_id, start_date, end_date
    )

    # Extract unique names and dates within the range
    names = sorted(set(item["full_name"] for item in attendance))
    dates = sorted(set(item["date"] for item in attendance))

    # Build a lookup dictionary for quick access
    lookup = {(item["full_name"], item["date"]): item["status"] for item in attendance}

    # Calculate previous and next start dates
    prev_start_date = (start_date - timedelta(days=30)).strftime("%Y-%m-%d")
    next_start_date = (start_date + timedelta(days=30)).strftime("%Y-%m-%d")

    return render_template(
        "view_attendance.html",
        names=names,
        dates=dates,
        lookup=lookup,
        class_data=class_data,
        prev_start_date=prev_start_date,
        next_start_date=next_start_date,
        current_period=f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}",
    )


@app.route("/view_payments/<int:class_id>")
def view_payments(class_id):
    # Get the start_date from the query string or default to the current date
    start_date_str = request.args.get("start_date", None)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    else:
        start_date = datetime.today().replace(day=1)  # First day of the current month

    # Calculate the end_date (3 months from start_date)
    end_date = start_date + timedelta(days=90)  # Approx. 3 months

    # Fetch class data and payments filtered by date range
    class_data = model.get_class(class_id)
    payments = model.get_class_payments_in_date_range(class_id, start_date, end_date)

    # Extract unique names and dates within the range
    names = sorted(set(item["full_name"] for item in payments))
    dates = sorted(set(item["date"] for item in payments))

    # Build a lookup dictionary for quick access
    lookup = {(item["full_name"], item["date"]): item["paid"] for item in payments}

    # Calculate previous and next start dates
    prev_start_date = (start_date - timedelta(days=90)).strftime("%Y-%m-%d")
    next_start_date = (start_date + timedelta(days=90)).strftime("%Y-%m-%d")

    return render_template(
        "view_payments.html",
        names=names,
        dates=dates,
        lookup=lookup,
        class_data=class_data,
        prev_start_date=prev_start_date,
        next_start_date=next_start_date,
        current_period=f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}",
    )


app.run(debug=True, host="0.0.0.0")
