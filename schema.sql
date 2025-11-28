CREATE DATABASE IF NOT EXISTS loan_management CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE loan_management;

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role ENUM('borrower','admin') NOT NULL
);

CREATE TABLE loans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  principal DECIMAL(12,2) NOT NULL,
  annual_rate DECIMAL(5,2) NOT NULL,
  term_months INT NOT NULL,
  monthly_emi DECIMAL(12,2) NOT NULL,
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE payments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  loan_id INT NOT NULL,
  amount DECIMAL(12,2) NOT NULL,
  payment_date DATE NOT NULL,
  FOREIGN KEY (loan_id) REFERENCES loans(id)
);
