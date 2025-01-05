from datetime import datetime
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

    def add_class(self, class_name, teacher_ids, package_id, day_of_week, time_of_day):
        dbcursor = self.__conn.cursor(dictionary=True)

        # Insert the class with schedule details
        dbcursor.execute(
            "INSERT INTO classes (class_name, day_of_week, time_of_day) VALUES (%s, %s, %s)",
            (class_name, day_of_week, time_of_day),
        )
        new_class_id = dbcursor.lastrowid

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

        dbcursor.execute(
            "SELECT sc.student_id AS student_id, s.full_name AS full_name, a.status AS status, a.notes AS notes, sp.paid AS paid "
            "FROM attendance a "
            "JOIN student_classes sc ON a.student_class_id = sc.student_class_id "
            "JOIN students s ON sc.student_id = s.student_id "
            "LEFT JOIN package_classes pc ON sc.class_id = pc.class_id "
            "LEFT JOIN student_monthly_package_payments sp ON sp.package_id = pc.package_id AND sp.student_id = sc.student_id AND YEAR(sp.payment_month) = %s AND MONTH(sp.payment_month) = %s "
            "WHERE sc.class_id = %s AND a.attendance_date = %s",
            (
                attendance_date.year,
                attendance_date.month,
                class_id,
                attendance_date.strftime("%Y-%m-%d"),
            ),
        )
        records = dbcursor.fetchall()
        dbcursor.close()

        return records

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
        dbcursor = self.__conn.cursor(dictionary=True)
        students = self.get_class_students(class_id)

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

        self.__conn.commit()
        dbcursor.close()

    def update_attendance_field(
        self, class_id, student_id, field, value, attendance_date
    ):
        """
        attendance_records: List of dictionaries in the format:
        [{'student_id': 1, 'status': 'Present', 'notes': 'On time'}, ...]
        """

        dbcursor = self.__conn.cursor(dictionary=True)
        if field == "paid":
            value = True if value == "1" else False
            print("paying", value)
            payment_month = datetime(
                attendance_date.year, attendance_date.month, 1
            ).strftime("%Y-%m-%d")

            dbcursor.execute(
                "SELECT package_id FROM package_classes WHERE class_id = %s",
                (class_id,),
            )
            package_id = dbcursor.fetchone()["package_id"]
            dbcursor.execute(
                "UPDATE student_monthly_package_payments SET paid = %s WHERE student_id = %s AND package_id = %s AND payment_month = %s",
                (value, student_id, package_id, payment_month),
            )
        else:
            print("attending")
            # Get the `student_class_id` for the student and class
            dbcursor.execute(
                "SELECT student_class_id FROM student_classes WHERE student_id = %s AND class_id = %s",
                (student_id, class_id),
            )

            student_class_id = dbcursor.fetchone()["student_class_id"]
            print(student_class_id)

            # Update the attendance recordallowed_fields = ["notes", "status", "remarks"]  # Add valid column names here
            if field not in ["notes", "status"]:
                raise ValueError("Invalid column name")
            query = f"UPDATE attendance SET {field} = %s WHERE student_class_id = %s AND attendance_date = %s"
            dbcursor.execute(
                query,
                (
                    value,
                    student_class_id,
                    attendance_date.strftime("%Y-%m-%d"),
                ),
            )

        self.__conn.commit()
        dbcursor.close()

    def mark_attendance(self, class_id, attendance_date, attendance_records):
        """
        attendance_records: List of dictionaries in the format:
        [{'student_id': 1, 'status': 'Present', 'notes': 'On time'}, ...]
        """
        payment_month = datetime(
            attendance_date.year, attendance_date.month, 1
        ).strftime("%Y-%m-%d")

        dbcursor = self.__conn.cursor(dictionary=True)

        dbcursor.execute(
            "SELECT package_id FROM package_classes WHERE class_id = %s",
            (class_id,),
        )
        package_id = dbcursor.fetchone()["package_id"]

        for record in attendance_records:
            # Get the `student_class_id` for the student and class
            dbcursor.execute(
                "SELECT student_class_id FROM student_classes WHERE student_id = %s AND class_id = %s",
                (record["student_id"], class_id),
            )

            student_class_id = dbcursor.fetchone()["student_class_id"]

            # Update the attendance record
            dbcursor.execute(
                "UPDATE attendance SET status = %s, notes = %s WHERE student_class_id = %s AND attendance_date = %s",
                (
                    record["status"],
                    record.get("notes", ""),
                    student_class_id,
                    attendance_date.strftime("%Y-%m-%d"),
                ),
            )
            dbcursor.execute(
                "UPDATE student_monthly_package_payments SET paid = %s WHERE student_id = %s AND package_id = %s AND payment_month = %s",
                (record["paid"], record["student_id"], package_id, payment_month),
            )

        self.__conn.commit()
        dbcursor.close()


model = Model()
