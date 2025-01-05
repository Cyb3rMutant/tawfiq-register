ALTER DATABASE register
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create `students` table
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female') NOT NULL,
    phone_number VARCHAR(15) NOT NULL
)ENGINE=InnoDB;

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
)ENGINE=InnoDB;

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
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    time_of_day TIME NOT NULL
)ENGINE=InnoDB;

-- Insert predefined class options
INSERT INTO classes (class_name, day_of_week, time_of_day) VALUES 
('Islamic studies', "Sunday", "18:00"),
('Quran', "Sunday", "17:00"),
('Arabic', "Saturday", "18:00");

-- Create `teachers` table
CREATE TABLE teachers (
    teacher_id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_name VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
    phone_number VARCHAR(15)
)ENGINE=InnoDB;

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

INSERT INTO teacher_classes (teacher_id, class_id) VALUES 
  (1, 2),
  (2, 1);

-- Create `student_classes` table (many-to-many relationship)
CREATE TABLE student_classes (
    student_class_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(class_id) ON DELETE CASCADE
);

INSERT INTO student_classes (student_id, class_id) VALUES
  (1, 2),
  (2, 2),
  (2, 1),
  (1, 1),
  (2, 3);

CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL DEFAULT 'Absent',
    notes VARCHAR(255),
    FOREIGN KEY (student_class_id) REFERENCES student_classes(student_class_id) ON DELETE CASCADE
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

INSERT INTO package_classes ( package_id, class_id) VALUES
  (1, 1),
  (1, 2),
  (2, 3);

-- -- Track student purchases of packages
-- CREATE TABLE student_packages (
--     student_package_id INT AUTO_INCREMENT PRIMARY KEY,
--     student_id INT NOT NULL,
--     package_id INT NOT NULL,
--     FOREIGN KEY (student_id) REFERENCES students(student_id),
--     FOREIGN KEY (package_id) REFERENCES packages(package_id)
-- );
--
-- INSERT INTO student_packages (student_id, package_id) VALUES
--   (1, 1),
--   (2, 1);

CREATE TABLE student_monthly_package_payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    package_id INT NOT NULL,
    payment_month DATE NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (package_id) REFERENCES packages(package_id)
);

