-- Create `payers` table
CREATE TABLE payers (
    payer_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    phone_number VARCHAR(15) NOT NULL
);

INSERT INTO payers (full_name, phone_number) VALUES
  ("Muawiya Abu-Hummos", "00962795685407"),
  ("umar", "0795685407");

-- Create `students` table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    payer_id INT NOT NULL,
    full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    FOREIGN KEY (payer_id) REFERENCES payers(payer_id)
);

INSERT INTO students (full_name, age, gender, phone_number, payer_id) VALUES
  ("Yazeed Abu-Hummos", 22, "Male", "7742903241", 1),
  ("Hamza Abu-Hummos", 20, "Male", "7742903241", 1),
  ("umar", 20, "Male", "0795685407", 2);

-- Define packages and their prices
CREATE TABLE packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(255) NOT NULL,
    price INT NOT NULL
);

INSERT INTO packages ( package_name, price) VALUES
  ("big packcage", 20),
  ("small package", 5);

-- Create `classes` table
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    package_id INT NOT NULL,
    class_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    FOREIGN KEY(package_id) REFERENCES packages(package_id)
);

CREATE TABLE days_of_week (
  day_id INT AUTO_INCREMENT PRIMARY KEY,
  day_name ENUM('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday') NOT NULL UNIQUE
);

INSERT INTO days_of_week (
  day_name
) VALUES ('Sunday'), ('Monday'), ('Tuesday'), ('Wednesday'), ('Thursday'), ('Friday'), ('Saturday');

-- Create `classes_times` table
CREATE TABLE class_times (
  class_time_id INT AUTO_INCREMENT PRIMARY KEY,
  class_id INT NOT NULL,
  day_id INT NOT NULL,
  time TIME NOT NULL,
  FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
  FOREIGN KEY (day_id) REFERENCES days_of_week(day_id) ON DELETE CASCADE
);

-- Create `teachers` table
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    phone_number VARCHAR(15)
);

INSERT INTO teachers (teacher_name, phone_number) VALUES 
  ("anas", "2093493247"),
  ("Sheikh Sheikh Mukhtar AbdurRahman", "2093493247");

-- Create `teacher_classes` table (many-to-many relationship)
CREATE TABLE teacher_classes (
    teacher_class_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);

-- Create `student_classes` table (many-to-many relationship)
CREATE TABLE student_classes (
    student_class_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);

CREATE TABLE class_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    class_time_id INT NOT NULL,
    session_date DATE NOT NULL,
    FOREIGN KEY (class_time_id) REFERENCES class_times(class_time_id) ON DELETE CASCADE,
    UNIQUE (class_time_id, session_date) -- prevent duplicates
);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    session_id INT NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL DEFAULT 'Absent',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES class_sessions(session_id) ON DELETE CASCADE,
    UNIQUE (student_id, session_id) -- prevent duplicate entries
);

CREATE TABLE field_types (
  	field_type_id INT AUTO_INCREMENT PRIMARY KEY,
  	field_type_name VARCHAR(23),
  	field_type_defaults BOOL
);

INSERT INTO field_types (field_type_name, field_type_defaults) VALUES
("text", false),
("checkbox", true),
("radio", true);
 
CREATE TABLE class_fields (
  	class_field_id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    field_type_id INT NOT NULL,
    field_name VARCHAR(50) NOT NULL,
  	field_defaults JSON NOT NULL, 
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE,
    FOREIGN KEY (field_type_id) REFERENCES field_types(field_type_id) ON DELETE CASCADE
);

CREATE TABLE attendance_fields (
  	attendance_field_id INT AUTO_INCREMENT PRIMARY KEY,
  	attendance_id INT NOT NULL,
  	class_field_id INT NOT NULL,
  	field_value JSON,
    FOREIGN KEY (attendance_id) REFERENCES attendance(attendance_id) ON DELETE CASCADE,
    FOREIGN KEY (class_field_id) REFERENCES class_fields(class_field_id) ON DELETE CASCADE
);

CREATE TABLE student_monthly_package_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    package_id INT NOT NULL,
    payment_month DATE NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (package_id) REFERENCES packages(package_id)
);
