-- Create the database
CREATE DATABASE IF NOT EXISTS heal_id;

-- Use the database
USE heal_id;

-- Create tables
CREATE TABLE IF NOT EXISTS Address (
    Address_ID INT AUTO_INCREMENT PRIMARY KEY,
    Street VARCHAR(255),
    City VARCHAR(100),
    State VARCHAR(100),
    Zip_Code VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Personal_Information (
    Aadhar_number VARCHAR(12) PRIMARY KEY,
    Name VARCHAR(100),
    Date_of_Birth DATE,
    Gender ENUM('Male', 'Female', 'Other'),
    Phone_Number VARCHAR(15),
    Email VARCHAR(100),
    Address_ID INT,
    Emergency_Contact_Name VARCHAR(100),
    Emergency_Contact_Phone VARCHAR(15),
    FOREIGN KEY (Address_ID) REFERENCES Address(Address_ID)
);

CREATE TABLE IF NOT EXISTS Vital_Signs (
    Aadhar_number VARCHAR(12) PRIMARY KEY,
    Blood_Pressure VARCHAR(20),
    Heart_Rate INT,
    Respiratory_Rate INT,
    Body_Temperature DECIMAL(4,2),
    Height DECIMAL(5,2),
    Weight DECIMAL(5,2),
    BMI DECIMAL(4,2),
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Medical_History (
    Aadhar_number VARCHAR(12) PRIMARY KEY,
    Family_Medical_History TEXT,
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Allergies (
    Allergy_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Allergy VARCHAR(100),
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Chronic_Conditions (
    Condition_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Condition_Name VARCHAR(100),
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Past_Surgeries (
    Surgery_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Surgery VARCHAR(100),
    Surgery_Date DATE,
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Immunization_Records (
    Immunization_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Immunization VARCHAR(100),
    Immunization_Date DATE,
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Lifestyle_Factors (
    Aadhar_number VARCHAR(12) PRIMARY KEY,
    Smoking_Status ENUM('Non-smoker', 'Former smoker', 'Current smoker'),
    Alcohol_Consumption ENUM('None', 'Occasional', 'Moderate', 'Heavy'),
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Doctors (
    Doctor_ID INT AUTO_INCREMENT PRIMARY KEY,
    Doctor_Name VARCHAR(100),
    Specialization VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Doctor_Visit (
    Visiting_id INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Visit_Date DATE,
    Visit_Reason TEXT,
    Doctor_ID INT,
    Diagnosis TEXT,
    Treatment_Plan TEXT,
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number),
    FOREIGN KEY (Doctor_ID) REFERENCES Doctors(Doctor_ID)
);

CREATE TABLE IF NOT EXISTS Laboratory_Results (
    Visiting_id INT,
    Aadhar_number VARCHAR(12),
    Test_Name VARCHAR(100),
    PDF_File VARCHAR(255),
    PRIMARY KEY (Visiting_id, Test_Name),
    FOREIGN KEY (Aadhar_number, Visiting_id) REFERENCES Doctor_Visit(Aadhar_number, Visiting_id)
);

CREATE TABLE IF NOT EXISTS Test_Results (
    Visiting_id INT,
    Test_Name VARCHAR(100),
    Test_Result TEXT,
    PRIMARY KEY (Visiting_id, Test_Name),
    FOREIGN KEY (Visiting_id, Test_Name) REFERENCES Laboratory_Results(Visiting_id, Test_Name)
);

CREATE TABLE IF NOT EXISTS Exercise_Habits (
    Exercise_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Exercise_Type VARCHAR(100),
    Frequency VARCHAR(50),
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Diet_Information (
    Diet_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Diet_Type VARCHAR(100),
    Diet_Details TEXT,
    FOREIGN KEY (Aadhar_number) REFERENCES Personal_Information(Aadhar_number)
);

CREATE TABLE IF NOT EXISTS Personal_Information_Audit (
    Audit_ID INT AUTO_INCREMENT PRIMARY KEY,
    Aadhar_number VARCHAR(12),
    Changed_Column VARCHAR(30),
    Old_Value VARCHAR(255),
    New_Value VARCHAR(255),
    Changed_By VARCHAR(30),
    Change_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
