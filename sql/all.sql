-- Create the database
--trying to commit (krishna)
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
    Aadhar_number VARCHAR(12),
    Visiting_id INT AUTO_INCREMENT,
    Visit_Date DATE,
    Visit_Reason TEXT,
    Doctor_ID INT,
    Diagnosis TEXT,
    Treatment_Plan TEXT,
    PRIMARY KEY (Aadhar_number, Visiting_id),
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
-- DML Queries

-- 1. Register a new patient
INSERT INTO Address (Street, City, State, Zip_Code)
VALUES ('123 MG Road', 'Pune', 'Maharashtra', '411001');

INSERT INTO Personal_Information (Aadhar_number, Name, Date_of_Birth, Gender, Phone_Number, Email, Address_ID)
VALUES ('123456789012', 'Rahul Sharma', '2005-05-15', 'Male', '9876543210', 'rahul.sharma@email.com', LAST_INSERT_ID());

-- 2. Update patient contact information
UPDATE Personal_Information
SET Phone_Number = '9876543211', Email = 'rahul.sharma.new@email.com'
WHERE Aadhar_number = '123456789012';

-- 3. Record patient vital signs
INSERT INTO Vital_Signs (Aadhar_number, Blood_Pressure, Heart_Rate, Respiratory_Rate, Body_Temperature, Height, Weight, BMI)
VALUES ('123456789012', '120/80', 72, 16, 37.0, 175.0, 70.0, 22.9)
ON DUPLICATE KEY UPDATE
Blood_Pressure = '120/80', Heart_Rate = 72, Respiratory_Rate = 16, Body_Temperature = 37.0, Height = 175.0, Weight = 70.0, BMI = 22.9;

-- 4. Add patient allergy
INSERT INTO Allergies (Aadhar_number, Allergy)
VALUES ('123456789012', 'Peanuts');

-- 5. Retrieve complete patient medical history
SELECT 
    pi.Name, 
    mh.Family_Medical_History,
    GROUP_CONCAT(DISTINCT cc.Condition_Name) AS Chronic_Conditions,
    GROUP_CONCAT(DISTINCT a.Allergy) AS Allergies,
    GROUP_CONCAT(DISTINCT CONCAT(ps.Surgery, ' (', ps.Surgery_Date, ')')) AS Past_Surgeries
FROM Personal_Information pi
LEFT JOIN Medical_History mh ON pi.Aadhar_number = mh.Aadhar_number
LEFT JOIN Chronic_Conditions cc ON pi.Aadhar_number = cc.Aadhar_number
LEFT JOIN Allergies a ON pi.Aadhar_number = a.Aadhar_number
LEFT JOIN Past_Surgeries ps ON pi.Aadhar_number = ps.Aadhar_number
WHERE pi.Aadhar_number = '123456789012'
GROUP BY pi.Aadhar_number;


-- insert doctor
INSERT INTO Doctors (Doctor_Name, Specialization) VALUES ('Dr. Krishna', 'General Practitioner');


-- 6. Record doctor visit details
INSERT INTO Doctor_Visit (Aadhar_number, Visiting_id, Visit_Date, Visit_Reason, Doctor_ID, Diagnosis, Treatment_Plan)
VALUES ('123456789012', 1, CURDATE(), 'Annual checkup', 1, 'Healthy', 'Continue current lifestyle');

-- 7. Update patient lifestyle factors
UPDATE Lifestyle_Factors
SET Smoking_Status = 'Non-smoker', Alcohol_Consumption = 'Occasional'
WHERE Aadhar_number = '123456789012';

-- 8. Add laboratory test results
INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name, PDF_File)
VALUES (1, '123456789012', 'Blood Test', 'blood_test_results.pdf');

INSERT INTO Test_Results (Visiting_id, Test_Name, Test_Result)
VALUES (1, 'Blood Test', 'Hemoglobin: 14.5 g/dL, WBC: 7500/μL, Platelets: 250,000/μL');

-- 9. Retrieve patient visit history with lab results
SELECT 
    dv.Visit_Date, 
    dv.Visit_Reason, 
    dv.Diagnosis, 
    lr.Test_Name, 
    tr.Test_Result
FROM Doctor_Visit dv
LEFT JOIN Laboratory_Results lr ON dv.Visiting_id = lr.Visiting_id AND dv.Aadhar_number = lr.Aadhar_number
LEFT JOIN Test_Results tr ON lr.Visiting_id = tr.Visiting_id AND lr.Test_Name = tr.Test_Name
WHERE dv.Aadhar_number = '123456789012'
AND dv.Visit_Date BETWEEN '2023-01-01' AND '2023-12-31'
ORDER BY dv.Visit_Date DESC;

-- 10. Generate immunization update report
SELECT 
    pi.Name, 
    pi.Phone_Number, 
    ir.Immunization, 
    ir.Immunization_Date,
    DATE_ADD(ir.Immunization_Date, INTERVAL 1 YEAR) AS Next_Due_Date
FROM Personal_Information pi
JOIN Immunization_Records ir ON pi.Aadhar_number = ir.Aadhar_number
WHERE DATE_ADD(ir.Immunization_Date, INTERVAL 1 YEAR) <= CURDATE()
ORDER BY Next_Due_Date;
DELIMITER //

-- Function 1: Calculate age based on Date of Birth
CREATE FUNCTION calculate_age(p_dob DATE) 
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_age INT;
    SET v_age = FLOOR(DATEDIFF(CURDATE(), p_dob) / 365.25);
    RETURN v_age;
END //

-- Function 2: Determine health risk level
CREATE FUNCTION determine_health_risk(p_aadhar_number VARCHAR(12)) 
RETURNS VARCHAR(20)
READS SQL DATA
BEGIN
    DECLARE v_risk_level VARCHAR(20);
    DECLARE v_bmi DECIMAL(4,2);
    DECLARE v_systolic INT;
    DECLARE v_diastolic INT;
    DECLARE v_chronic_condition_count INT;
    DECLARE v_smoking_status VARCHAR(20);
    DECLARE v_alcohol_consumption VARCHAR(20);
    
    -- Get BMI
    SELECT BMI INTO v_bmi
    FROM Vital_Signs
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Get blood pressure
    SELECT 
        CAST(SUBSTRING_INDEX(Blood_Pressure, '/', 1) AS UNSIGNED) AS systolic,
        CAST(SUBSTRING_INDEX(Blood_Pressure, '/', -1) AS UNSIGNED) AS diastolic
    INTO v_systolic, v_diastolic
    FROM Vital_Signs
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Count chronic conditions
    SELECT COUNT(*) INTO v_chronic_condition_count
    FROM Chronic_Conditions
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Get lifestyle factors
    SELECT Smoking_Status, Alcohol_Consumption
    INTO v_smoking_status, v_alcohol_consumption
    FROM Lifestyle_Factors
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Determine risk level
    IF v_bmi > 30 OR v_systolic > 140 OR v_diastolic > 90 OR
       v_chronic_condition_count > 2 OR v_smoking_status = 'Current smoker' OR
       v_alcohol_consumption = 'Heavy' THEN
        SET v_risk_level = 'High';
    ELSEIF v_bmi > 25 OR v_systolic > 120 OR v_diastolic > 80 OR
           v_chronic_condition_count > 0 OR v_smoking_status = 'Former smoker' OR
           v_alcohol_consumption = 'Moderate' THEN
        SET v_risk_level = 'Moderate';
    ELSE
        SET v_risk_level = 'Low';
    END IF;
    
    RETURN v_risk_level;
END //

DELIMITER ;
DELIMITER //

-- Procedure 1: Update BMI for all patients
CREATE PROCEDURE update_all_patient_bmi()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_aadhar_number VARCHAR(12);
    DECLARE v_height DECIMAL(5,2);
    DECLARE v_weight DECIMAL(5,2);
    DECLARE v_bmi DECIMAL(5,2);
    
    DECLARE patient_cursor CURSOR FOR
        SELECT Aadhar_number, Height, Weight
        FROM Vital_Signs
        WHERE Height IS NOT NULL AND Weight IS NOT NULL;
    
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN patient_cursor;
    
    read_loop: LOOP
        FETCH patient_cursor INTO v_aadhar_number, v_height, v_weight;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Calculate BMI: weight (kg) / (height (m))^2
        SET v_bmi = v_weight / POWER(v_height / 100, 2);
        
        -- Update BMI in Vital_Signs table
        UPDATE Vital_Signs
        SET BMI = ROUND(v_bmi, 2)
        WHERE Aadhar_number = v_aadhar_number;
    END LOOP;
    
    CLOSE patient_cursor;
    
    SELECT 'BMI updated for all patients.' AS message;
END //

-- Procedure 2: Generate health report for a patient
CREATE PROCEDURE generate_health_report(IN p_aadhar_number VARCHAR(12))
BEGIN
    DECLARE v_patient_name VARCHAR(100);
    DECLARE v_dob DATE;
    DECLARE v_gender VARCHAR(10);
    DECLARE v_blood_pressure VARCHAR(20);
    DECLARE v_heart_rate INT;
    DECLARE v_bmi DECIMAL(4,2);
    
    -- Fetch patient information
    SELECT Name, Date_of_Birth, Gender
    INTO v_patient_name, v_dob, v_gender
    FROM Personal_Information
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Fetch vital signs
    SELECT Blood_Pressure, Heart_Rate, BMI
    INTO v_blood_pressure, v_heart_rate, v_bmi
    FROM Vital_Signs
    WHERE Aadhar_number = p_aadhar_number;
    
    -- Generate report
    SELECT 'Patient Information' AS section, 
           CONCAT('Name: ', v_patient_name) AS details
    UNION ALL
    SELECT 'Patient Information', 
           CONCAT('Date of Birth: ', DATE_FORMAT(v_dob, '%d-%b-%Y'))
    UNION ALL
    SELECT 'Patient Information', 
           CONCAT('Gender: ', v_gender)
    UNION ALL
    SELECT 'Vital Signs', 
           CONCAT('Blood Pressure: ', v_blood_pressure)
    UNION ALL
    SELECT 'Vital Signs', 
           CONCAT('Heart Rate: ', v_heart_rate)
    UNION ALL
    SELECT 'Vital Signs', 
           CONCAT('BMI: ', v_bmi);

    SELECT 'Medical History' AS section, 
           Family_Medical_History AS details
    FROM Medical_History
    WHERE Aadhar_number = p_aadhar_number;

    SELECT 'Allergies' AS section, 
           GROUP_CONCAT(Allergy SEPARATOR ', ') AS details
    FROM Allergies
    WHERE Aadhar_number = p_aadhar_number;

    SELECT 'Chronic Conditions' AS section, 
           GROUP_CONCAT(Condition_Name SEPARATOR ', ') AS details
    FROM Chronic_Conditions
    WHERE Aadhar_number = p_aadhar_number;

    SELECT 'Recent Doctor Visits' AS section,
           CONCAT(
               'Date: ', DATE_FORMAT(Visit_Date, '%d-%b-%Y'), '\n',
               'Reason: ', Visit_Reason, '\n',
               'Diagnosis: ', Diagnosis, '\n',
               'Treatment: ', Treatment_Plan
           ) AS details
    FROM Doctor_Visit
    WHERE Aadhar_number = p_aadhar_number
    ORDER BY Visit_Date DESC
    LIMIT 5;
END //

DELIMITER ;
DELIMITER //

-- Trigger 1: Log changes to patient personal information
CREATE TRIGGER trg_audit_personal_info
AFTER UPDATE ON Personal_Information
FOR EACH ROW
BEGIN
    IF OLD.Name != NEW.Name THEN
        INSERT INTO Personal_Information_Audit (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Name', OLD.Name, NEW.Name, USER());
    END IF;
    
    IF OLD.Date_of_Birth != NEW.Date_of_Birth THEN
        INSERT INTO Personal_Information_Audit (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Date_of_Birth', DATE_FORMAT(OLD.Date_of_Birth, '%Y-%m-%d'), DATE_FORMAT(NEW.Date_of_Birth, '%Y-%m-%d'), USER());
    END IF;
    
    IF OLD.Gender != NEW.Gender THEN
        INSERT INTO Personal_Information_Audit (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Gender', OLD.Gender, NEW.Gender, USER());
    END IF;
    
    IF OLD.Phone_Number != NEW.Phone_Number THEN
        INSERT INTO Personal_Information_Audit (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Phone_Number', OLD.Phone_Number, NEW.Phone_Number, USER());
    END IF;
    
    IF OLD.Email != NEW.Email THEN
        INSERT INTO Personal_Information_Audit (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Email', OLD.Email, NEW.Email, USER());
    END IF;
END //

-- Trigger 2: Automatically update BMI when height or weight changes
CREATE TRIGGER trg_update_bmi
BEFORE UPDATE ON Vital_Signs
FOR EACH ROW
BEGIN
    IF NEW.Height IS NOT NULL AND NEW.Weight IS NOT NULL THEN
        -- Calculate BMI: weight (kg) / (height (m))^2
        SET NEW.BMI = ROUND(NEW.Weight / POWER(NEW.Height / 100, 2), 2);
    ELSE
        SET NEW.BMI = NULL;
    END IF;
END //

DELIMITER ;
