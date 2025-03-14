-- Create `students` table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    phone_number VARCHAR(15) NOT NULL
);

INSERT INTO students (full_name, age, gender, phone_number) VALUES
  ("Yazeed Abu-Hummos", 22, "Male", "7742903241"),
  ("umar", 20, "Male", "0795685407");

-- Create `emergency_contacts` table
CREATE TABLE emergency_contacts (
    contact_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    contact_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    contact_phone_number VARCHAR(15) NOT NULL,
    relationship VARCHAR(50) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Create `special_requirements` table
CREATE TABLE special_requirements (
    requirement_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    requirement TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Create `classes` table
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    days_of_week CHAR(7) NOT NULL,
    time_of_day TIME NOT NULL
);


-- Create `teachers` table
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    phone_number VARCHAR(15)
);

INSERT INTO teachers (teacher_name, phone_number) VALUES 
  ("Ustadh Anas Abdelsami", "2093493247"),
  ("Sheikh Abu-Thaabit", "2093493247");

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

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL DEFAULT 'Absent',
    FOREIGN KEY (student_class_id) REFERENCES student_classes(student_class_id) ON DELETE CASCADE
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

-- Define packages and their prices
CREATE TABLE packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    package_name VARCHAR(255) NOT NULL,
    price INT NOT NULL
);

INSERT INTO packages ( package_name, price) VALUES
  ("big packcage", 20),
  ("small package", 5);

-- Link packages to classes
CREATE TABLE package_classes (
    student_class_id INT AUTO_INCREMENT PRIMARY KEY,
    package_id INT NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (package_id) REFERENCES packages(package_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
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

