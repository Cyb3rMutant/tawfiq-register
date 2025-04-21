from datetime import datetime
import json
import mysql.connector


class Model:

    def __init__(self):
        self.__conn = mysql.connector.connect(
            host="localhost",
            # host="db",
            user="root",
            password="p",
            database="register",
        )

    def get_field_types(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM field_types")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_payers(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM payers")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_students(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM students")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def add_payer(self, full_name, phone_number):
        dbcursor = self.__conn.cursor(dictionary=True)

        # Insert the class with schedule details
        dbcursor.execute(
            "INSERT INTO payers (full_name, phone_number) VALUES (%s, %s)",
            (full_name, phone_number),
        )
        id = dbcursor.lastrowid

        self.__conn.commit()
        dbcursor.close()
        return id

    def add_student(self, full_name, age, gender, phone_number, classes, payer_id):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "INSERT INTO students (full_name, age, gender, phone_number, payer_id) VALUES (%s, %s, %s, %s, %s)",
            (
                full_name,
                age,
                gender,
                phone_number,
                payer_id,
            ),
        )
        new_student_id = dbcursor.lastrowid

        for class_id in classes:
            dbcursor.execute(
                "INSERT INTO student_classes(student_id, class_id) VALUES (%s, %s)",
                (new_student_id, class_id),
            )

        self.__conn.commit()
        dbcursor.close()

    def get_packages(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM packages")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_package(self, package_id):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM packages WHERE package_id = %s", (package_id,))
        data = dbcursor.fetchone()
        dbcursor.close()
        return data

    def add_package(self, package_name, price):
        dbcursor = self.__conn.cursor(dictionary=True)

        # Insert the class with schedule details
        dbcursor.execute(
            "INSERT INTO packages (package_name, price) VALUES (%s, %s)",
            (package_name, price),
        )

        self.__conn.commit()
        dbcursor.close()

    def get_teachers(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM teachers")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_teacher(self, name=None):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM teachers WHERE teacher_name = %s", (name,))
        data = dbcursor.fetchone()
        dbcursor.close()
        return data

    def add_teacher(self, teacher_name, phone_number):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "INSERT INTO teachers (teacher_name, phone_number) VALUES (%s, %s)",
            (teacher_name, phone_number),
        )
        self.__conn.commit()
        dbcursor.close()

    def get_classes_with_fields(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT class_id, class_name FROM classes")
        classes = dbcursor.fetchall()
        for c in classes:
            dbcursor.execute(
                "SELECT class_field_id, field_type_id, field_name, field_defaults FROM class_fields WHERE class_id = %s",
                (c["class_id"],),
            )
            c["fields"] = dbcursor.fetchall()
        dbcursor.close()
        return classes

    def get_classes(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM classes")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_teacher_classes(self, teacher_id):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "SELECT c.class_id, c.class_name, c.days_of_week, c.time_of_day \
             FROM teacher_classes tc JOIN classes c ON tc.class_id = c.class_id \
             WHERE tc.teacher_id = %s",
            (teacher_id,),
        )
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def get_class(self, class_id):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM classes WHERE class_id = %s", (class_id,))
        data = dbcursor.fetchone()
        dbcursor.close()
        return data

    def get_class_payments(self, class_id, payment_month):
        payment_month = datetime(payment_month.year, payment_month.month, 1).strftime(
            "%Y-%m-%d"
        )
        print(payment_month)
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            """
            SELECT s.full_name AS student_name, p.package_name AS package_name, p.price AS price, smpp.paid AS paid 
            FROM student_classes sc
            JOIN students s ON sc.student_id = s.student_id
            JOIN classes c ON sc.class_id = c.class_id
            JOIN packages p ON c.package_id = p.package_id
            JOIN student_monthly_package_payments smpp ON smpp.student_id = s.student_id AND smpp.package_id = p.package_id AND smpp.payment_month = %s
            WHERE sc.class_id = %s;
            """,
            (payment_month, class_id),
        )
        data = dbcursor.fetchall()
        print(data, dbcursor.statement)
        dbcursor.close()
        return data

    def add_class(
        self, class_name, teacher_ids, package_id, days_of_week, time_of_day, fields
    ):
        dbcursor = self.__conn.cursor(dictionary=True)

        # Insert the class with schedule details
        dbcursor.execute(
            "INSERT INTO classes (class_name, days_of_week, time_of_day, package_id) VALUES (%s, %s, %s, %s)",
            (class_name, days_of_week, time_of_day, package_id),
        )
        new_class_id = dbcursor.lastrowid
        for field in fields:
            print(
                field,
                new_class_id,
                field["field_type_id"],
                field["field_name"],
                field["defaultValues"],
            )
            dbcursor.execute(
                "INSERT INTO class_fields (class_id, field_type_id, field_name, field_defaults) VALUES (%s, %s, %s, %s)",
                (
                    new_class_id,
                    field["field_type_id"],
                    field["field_name"],
                    field["defaultValues"],
                ),
            )

        # Link teachers to the class
        for teacher_id in teacher_ids:
            dbcursor.execute(
                "INSERT INTO teacher_classes (class_id, teacher_id) VALUES (%s, %s)",
                (new_class_id, teacher_id),
            )

        self.__conn.commit()
        dbcursor.close()

    def assign_students_to_class(self, class_id, student_ids):
        print(class_id, student_ids)
        dbcursor = self.__conn.cursor(dictionary=True)

        for student_id in student_ids:
            dbcursor.execute(
                "INSERT INTO student_classes (student_id, class_id) VALUES (%s, %s)",
                (student_id, class_id),
            )

        self.__conn.commit()
        dbcursor.close()

    def get_class_students(self, class_id):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "SELECT s.student_id, s.full_name "
            "FROM student_classes sc "
            "JOIN students s ON sc.student_id = s.student_id "
            "WHERE sc.class_id = %s",
            (class_id,),
        )
        students = dbcursor.fetchall()
        dbcursor.close()

        return students

    def get_package_payments_in_date_range(self, package_id, start_date, end_date):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT sp.student_id AS student_id, s.full_name AS full_name, sp.paid AS paid, sp.payment_month AS date, "
            "p.full_name AS payer_name, p.phone_number AS payer_phone_number "
            "FROM student_monthly_package_payments sp "
            "JOIN students s ON sp.student_id = s.student_id "
            "LEFT JOIN payers p ON s.payer_id = p.payer_id "
            "WHERE sp.package_id = %s AND sp.payment_month BETWEEN %s AND %s",
            (
                package_id,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            ),
        )

        records = dbcursor.fetchall()
        dbcursor.close()

        return records

    def get_class_payments_in_date_range(self, class_id, start_date, end_date):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT sc.student_id AS student_id, s.full_name AS full_name, sp.paid AS paid, sp.payment_month AS date, p.full_name AS payer_name, p.phone_number AS payer_phone_number "
            "FROM student_classes sc "
            "JOIN students s ON sc.student_id = s.student_id "
            "LEFT JOIN classes c ON sc.class_id = c.class_id "
            "LEFT JOIN student_monthly_package_payments sp ON sp.package_id = c.package_id AND sp.student_id = sc.student_id "
            "LEFT JOIN payers p ON s.payer_id = p.payer_id "
            "WHERE sc.class_id = %s AND sp.payment_month BETWEEN %s AND %s",
            (class_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        records = dbcursor.fetchall()
        dbcursor.close()

        return records

    def get_all_class_payments(self, class_id):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT sc.student_id AS student_id, s.full_name AS full_name, sp.paid AS paid, sp.payment_month AS date "
            "FROM student_classes sc "
            "JOIN students s ON sc.student_id = s.student_id "
            "LEFT JOIN classes c ON sc.class_id = c.class_id "
            "LEFT JOIN student_monthly_package_payments sp ON sp.package_id = c.package_id AND sp.student_id = sc.student_id "
            "WHERE sc.class_id = %s",
            (class_id,),
        )
        records = dbcursor.fetchall()
        dbcursor.close()

        return records

    def get_class_attendance_in_date_range(self, class_id, start_date, end_date):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT a.attendance_id, sc.student_id AS student_id, s.full_name AS full_name, a.status AS status, a.attendance_date AS date "
            "FROM attendance a "
            "JOIN student_classes sc ON a.student_class_id = sc.student_class_id "
            "JOIN students s ON sc.student_id = s.student_id "
            "WHERE sc.class_id = %s AND a.attendance_date BETWEEN %s AND %s "
            "ORDER BY date ASC",
            (class_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        records = dbcursor.fetchall()

        for record in records:
            dbcursor.execute(
                """
                SELECT af.field_value, 
                       cf.field_name, 
                       cf.field_defaults, 
                       ft.field_type_name 
                FROM attendance_fields af
                JOIN class_fields cf ON af.class_field_id = cf.class_field_id
                JOIN field_types ft ON cf.field_type_id = ft.field_type_id
                WHERE af.attendance_id = %s
                """,
                (record["attendance_id"],),
            )
            record["fields"] = dbcursor.fetchall()
            for f in record["fields"]:
                f["field_defaults"] = [
                    x for x in enumerate(json.loads(f["field_defaults"]))
                ]
                f["field_value"] = json.loads(f["field_value"])

        dbcursor.close()

        return records

    def get_attendance(self, class_id, attendance_date):

        dbcursor = self.__conn.cursor(dictionary=True)

        # Fetch attendance records
        dbcursor.execute(
            """
            SELECT s.full_name AS full_name, 
                   a.attendance_id AS attendance_id, 
                   a.status AS status, 
                   sp.payment_id AS payment_id,
                   sp.paid AS paid
            FROM attendance a
            JOIN student_classes sc ON a.student_class_id = sc.student_class_id
            JOIN students s ON sc.student_id = s.student_id
            LEFT JOIN classes c ON sc.class_id = c.class_id
            LEFT JOIN student_monthly_package_payments sp 
                ON sp.package_id = c.package_id 
                AND sp.student_id = sc.student_id 
                AND YEAR(sp.payment_month) = %s 
                AND MONTH(sp.payment_month) = %s
            WHERE sc.class_id = %s 
              AND a.attendance_date = %s
            """,
            (
                attendance_date.year,
                attendance_date.month,
                class_id,
                attendance_date.strftime("%Y-%m-%d"),
            ),
        )

        attendance_records = dbcursor.fetchall()

        # Fetch attendance field values for each attendance record
        for record in attendance_records:
            dbcursor.execute(
                """
                SELECT af.attendance_field_id, 
                       af.field_value, 
                       cf.class_field_id, 
                       cf.field_name, 
                       cf.field_defaults, 
                       ft.field_type_name 
                FROM attendance_fields af
                JOIN class_fields cf ON af.class_field_id = cf.class_field_id
                JOIN field_types ft ON cf.field_type_id = ft.field_type_id
                WHERE af.attendance_id = %s
                """,
                (record["attendance_id"],),
            )
            record["fields"] = dbcursor.fetchall()
            for f in record["fields"]:
                f["field_defaults"] = [
                    x for x in enumerate(json.loads(f["field_defaults"]))
                ]
                f["field_value"] = json.loads(f["field_value"])
            print(record["fields"])

        dbcursor.close()
        return attendance_records

    def init_payment_month(self, class_id, payment_month: datetime):
        payment_month = datetime(payment_month.year, payment_month.month, 1).strftime(
            "%Y-%m-%d"
        )
        dbcursor = self.__conn.cursor(dictionary=True)
        students = self.get_class_students(class_id)

        for student in students:
            # Get the `student_class_id` for the student and class
            dbcursor.execute(
                "SELECT package_id FROM classes WHERE class_id = %s",
                (class_id,),
            )
            package_id = dbcursor.fetchone()["package_id"]

            # Insert attendance record
            dbcursor.execute(
                "INSERT INTO student_monthly_package_payments (student_id, package_id, payment_month) VALUES (%s, %s, %s)",
                (student["student_id"], package_id, payment_month),
            )

        self.__conn.commit()
        dbcursor.close()

    def init_attendance_day(self, class_id, attendance_date):
        print("initing attendancd")

        dbcursor = self.__conn.cursor(dictionary=True)
        students = self.get_class_students(class_id)

        # Get all class fields for the class
        dbcursor.execute(
            "SELECT class_field_id, field_type_id, field_defaults FROM class_fields WHERE class_id = %s",
            (class_id,),
        )
        class_fields = dbcursor.fetchall()
        # Get field type mapping
        dbcursor.execute("SELECT field_type_id, field_type_name FROM field_types")
        field_types = {
            row["field_type_id"]: row["field_type_name"] for row in dbcursor.fetchall()
        }

        for student in students:
            # Get the `student_class_id` for the student and class
            dbcursor.execute(
                "SELECT student_class_id FROM student_classes WHERE student_id = %s AND class_id = %s",
                (student["student_id"], class_id),
            )
            student_class_id = dbcursor.fetchone()["student_class_id"]

            # Insert attendance record
            dbcursor.execute(
                "INSERT INTO attendance (student_class_id, attendance_date) VALUES (%s, %s)",
                (student_class_id, attendance_date.strftime("%Y-%m-%d")),
            )
            attendance_id = dbcursor.lastrowid  # Get the inserted attendance_id

            # Insert default values into attendance_fields
            for field in class_fields:
                field_type = field_types[field["field_type_id"]]

                if field_type == "text" or field_type == "checkbox":
                    default_value = []
                elif field_type == "radio":
                    default_value = [0]

                dbcursor.execute(
                    "INSERT INTO attendance_fields (attendance_id, class_field_id, field_value) VALUES (%s, %s, %s)",
                    (attendance_id, field["class_field_id"], json.dumps(default_value)),
                )

        self.__conn.commit()
        dbcursor.close()

    def update_attendance_field(self, field_id, field, value):
        """
        attendance_records: List of dictionaries in the format:
        [{'student_id': 1, 'status': 'Present', 'notes': 'On time'}, ...]
        """

        dbcursor = self.__conn.cursor(dictionary=True)
        if field == "student":
            dbcursor.execute(
                "UPDATE attendance SET status = %s WHERE attendance_id = %s",
                (value, field_id),
            )
        elif field == "paid":
            dbcursor.execute(
                "UPDATE student_monthly_package_payments SET paid = %s WHERE payment_id  = %s",
                (value == "on", field_id),
            )
        else:
            if field == "select":
                value = [int(value)]
            elif field == "checkbox":
                value = [int(v) for v in value.split(",")]
            elif field == "text":
                value = [value]

            print(field_id, field, value)
            dbcursor.execute(
                "UPDATE attendance_fields SET field_value = %s WHERE attendance_field_id = %s",
                (json.dumps(value), field_id),
            )
        self.__conn.commit()
        dbcursor.close()

    def mark_attendance(self, attendance_vals, payment_vals, field_vals):
        """
        attendance_records: List of dictionaries in the format:
        [{'student_id': 1, 'status': 'Present', 'notes': 'On time'}, ...]
        """
        dbcursor = self.__conn.cursor(dictionary=True)

        for id, val in attendance_vals.items():
            dbcursor.execute(
                "UPDATE attendance SET status = %s WHERE attendance_id = %s",
                (val, id),
            )
        for id, val in payment_vals.items():
            dbcursor.execute(
                "UPDATE student_monthly_package_payments SET paid = %s WHERE payment_id = %s",
                (val, id),
            )

        for id, val in field_vals.items():
            dbcursor.execute(
                "UPDATE attendance_fields SET field_value = %s WHERE attendance_field_id = %s",
                (json.dumps(val), id),
            )

        self.__conn.commit()
        dbcursor.close()

    def load_attendance_data(self, class_id, attendance_data):
        dbcursor = self.__conn.cursor(dictionary=True)

        # Get class fields and field type mappings
        dbcursor.execute(
            "SELECT class_field_id, field_type_id, field_defaults FROM class_fields WHERE class_id = %s",
            (class_id,),
        )
        class_fields = {row["class_field_id"]: row for row in dbcursor.fetchall()}

        dbcursor.execute("SELECT field_type_id, field_type_name FROM field_types")
        field_types = {
            row["field_type_id"]: row["field_type_name"] for row in dbcursor.fetchall()
        }

        # Process each attendance date
        for day in attendance_data:
            attendance_date = day["date"].strftime("%Y-%m-%d")

            for record in day["records"]:
                full_name = record["full_name"]

                # Get student_id
                dbcursor.execute(
                    "SELECT student_id FROM students WHERE full_name = %s", (full_name,)
                )
                student_row = dbcursor.fetchone()
                if not student_row:
                    print(f"Student {full_name} not found. Skipping.")
                    continue
                student_id = student_row["student_id"]

                # Get student_class_id
                dbcursor.execute(
                    "SELECT student_class_id FROM student_classes WHERE student_id = %s AND class_id = %s",
                    (student_id, class_id),
                )
                student_class_row = dbcursor.fetchone()
                if not student_class_row:
                    print(f"Student {full_name} is not in class {class_id}. Skipping.")
                    continue
                student_class_id = student_class_row["student_class_id"]

                # Insert attendance record
                dbcursor.execute(
                    "INSERT INTO attendance (student_class_id, attendance_date) VALUES (%s, %s)",
                    (student_class_id, attendance_date),
                )
                attendance_id = dbcursor.lastrowid

                # Process fields
                for field in record["fields"]:
                    field_id = field["field_id"]
                    field_value = field["field_value"]

                    if field_id == "attendance":
                        field_value = [field_value]  # Store as an array
                        dbcursor.execute(
                            "UPDATE attendance SET status = %s WHERE attendance_id = %s",
                            (field_value[0], attendance_id),
                        )
                        continue

                    # Convert field_id to int if it's not "attendance"
                    field_id = int(field_id)
                    if field_id not in class_fields:
                        print(
                            f"Field ID {field_id} not found for class {class_id}. Skipping."
                        )
                        continue

                    class_field = class_fields[field_id]
                    field_type = field_types[class_field["field_type_id"]]
                    field_defaults = json.loads(class_field["field_defaults"])

                    # Format field_value based on field type
                    if field_type == "text":
                        field_value = [field_value]
                    elif field_type in {"radio", "checkbox"}:
                        field_value = (
                            [field_defaults.index(field_value)]
                            if field_value in field_defaults
                            else []
                        )

                    # Insert into attendance_fields
                    dbcursor.execute(
                        "INSERT INTO attendance_fields (attendance_id, class_field_id, field_value) VALUES (%s, %s, %s)",
                        (attendance_id, field_id, json.dumps(field_value)),
                    )

        self.__conn.commit()
        dbcursor.close()


model = Model()
