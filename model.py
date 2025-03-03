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

    def get_students(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM students")
        data = dbcursor.fetchall()
        dbcursor.close()
        return data

    def add_student(
        self, full_name, age, gender, phone_number, classes, special_requirements=""
    ):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "INSERT INTO students (full_name, age, gender, phone_number) VALUES (%s, %s, %s, %s)",
            (
                full_name,
                age,
                gender,
                phone_number,
            ),
        )
        new_student_id = dbcursor.lastrowid

        if special_requirements:
            dbcursor.execute(
                "INSERT INTO special_requirements (student_id, requirement) VALUES (%s, %s)",
                (new_student_id, special_requirements),
            )

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

    def add_teacher(self, teacher_name, phone_number):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute(
            "INSERT INTO teachers (teacher_name, phone_number) VALUES (%s, %s)",
            (teacher_name, phone_number),
        )
        self.__conn.commit()
        dbcursor.close()

    def get_classes(self):
        dbcursor = self.__conn.cursor(dictionary=True)
        dbcursor.execute("SELECT * FROM classes")
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
            JOIN package_classes pc ON sc.class_id = pc.class_id
            JOIN packages p ON pc.package_id = p.package_id
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
            "INSERT INTO classes (class_name, days_of_week, time_of_day) VALUES (%s, %s, %s)",
            (class_name, days_of_week, time_of_day),
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

        dbcursor.execute(
            "INSERT INTO package_classes (package_id, class_id) VALUES (%s, %s)",
            (package_id, new_class_id),
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
        dbcursor.execute(
            "SELECT package_id FROM package_classes WHERE class_id = %s", (class_id,)
        )
        package_id = dbcursor.fetchone()["package_id"]

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

    def get_class_payments_in_date_range(self, class_id, start_date, end_date):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT sc.student_id AS student_id, s.full_name AS full_name, sp.paid AS paid, sp.payment_month AS date "
            "FROM student_classes sc "
            "JOIN students s ON sc.student_id = s.student_id "
            "LEFT JOIN package_classes pc ON sc.class_id = pc.class_id "
            "LEFT JOIN student_monthly_package_payments sp ON sp.package_id = pc.package_id AND sp.student_id = sc.student_id "
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
            "LEFT JOIN package_classes pc ON sc.class_id = pc.class_id "
            "LEFT JOIN student_monthly_package_payments sp ON sp.package_id = pc.package_id AND sp.student_id = sc.student_id "
            "WHERE sc.class_id = %s",
            (class_id,),
        )
        records = dbcursor.fetchall()
        dbcursor.close()

        return records

    def get_class_attendance_in_date_range(self, class_id, start_date, end_date):
        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT sc.student_id AS student_id, s.full_name AS full_name, a.status AS status, a.attendance_date AS date "
            "FROM attendance a "
            "JOIN student_classes sc ON a.student_class_id = sc.student_class_id "
            "JOIN students s ON sc.student_id = s.student_id "
            "WHERE sc.class_id = %s AND a.attendance_date BETWEEN %s AND %s "
            "ORDER BY date ASC",
            (class_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")),
        )
        records = dbcursor.fetchall()
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
            LEFT JOIN package_classes pc ON sc.class_id = pc.class_id
            LEFT JOIN student_monthly_package_payments sp 
                ON sp.package_id = pc.package_id 
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
            record["fields"] = (
                dbcursor.fetchall()
            )  # Attach attendance fields to each attendance record
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
                "SELECT package_id FROM package_classes WHERE class_id = %s",
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


model = Model()
