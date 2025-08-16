-- Function to calculate BMI
DELIMITER //
CREATE FUNCTION calculate_bmi(height_cm DECIMAL(5,2), weight_kg DECIMAL(5,2)) 
RETURNS DECIMAL(4,2)
DETERMINISTIC
BEGIN
    DECLARE bmi DECIMAL(4,2);
    SET bmi = weight_kg / POWER(height_cm/100, 2);
    RETURN ROUND(bmi, 2);
END //
DELIMITER ;

-- Function to calculate age
DELIMITER //
CREATE FUNCTION calculate_age(birth_date DATE)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN TIMESTAMPDIFF(YEAR, birth_date, CURDATE());
END //
DELIMITER ;

-- Procedure to update vital signs with automatic BMI calculation
DELIMITER //
CREATE PROCEDURE update_vital_signs(
    IN p_aadhar VARCHAR(12),
    IN p_blood_pressure VARCHAR(20),
    IN p_heart_rate INT,
    IN p_respiratory_rate INT,
    IN p_body_temperature DECIMAL(4,2),
    IN p_height DECIMAL(5,2),
    IN p_weight DECIMAL(5,2)
)
BEGIN
    DECLARE calculated_bmi DECIMAL(4,2);
    SET calculated_bmi = calculate_bmi(p_height, p_weight);
    
    REPLACE INTO Vital_Signs (
        Aadhar_number, Blood_Pressure, Heart_Rate, 
        Respiratory_Rate, Body_Temperature, 
        Height, Weight, BMI
    )
    VALUES (
        p_aadhar, p_blood_pressure, p_heart_rate,
        p_respiratory_rate, p_body_temperature,
        p_height, p_weight, calculated_bmi
    );
END //
DELIMITER ;

-- Procedure to register new patient
DELIMITER //
CREATE PROCEDURE register_patient(
    IN p_aadhar VARCHAR(12),
    IN p_name VARCHAR(100),
    IN p_dob DATE,
    IN p_gender VARCHAR(10),
    IN p_phone VARCHAR(15),
    IN p_email VARCHAR(100),
    IN p_street VARCHAR(255),
    IN p_city VARCHAR(100),
    IN p_state VARCHAR(100),
    IN p_zip VARCHAR(20),
    IN p_emergency_name VARCHAR(100),
    IN p_emergency_phone VARCHAR(15)
)
BEGIN
    DECLARE new_address_id INT;
    
    START TRANSACTION;
    
    -- Insert address
    INSERT INTO Address (Street, City, State, Zip_Code)
    VALUES (p_street, p_city, p_state, p_zip);
    
    SET new_address_id = LAST_INSERT_ID();
    
    -- Insert personal information
    INSERT INTO Personal_Information (
        Aadhar_number, Name, Date_of_Birth, Gender,
        Phone_Number, Email, Address_ID,
        Emergency_Contact_Name, Emergency_Contact_Phone
    )
    VALUES (
        p_aadhar, p_name, p_dob, p_gender,
        p_phone, p_email, new_address_id,
        p_emergency_name, p_emergency_phone
    );
    
    -- Initialize other related tables
    INSERT INTO Medical_History (Aadhar_number)
    VALUES (p_aadhar);
    
    INSERT INTO Lifestyle_Factors (Aadhar_number, Smoking_Status, Alcohol_Consumption)
    VALUES (p_aadhar, 'Non-smoker', 'None');
    
    COMMIT;
END //
DELIMITER ;

-- Procedure to record doctor visit
DELIMITER //
CREATE PROCEDURE record_doctor_visit(
    IN p_aadhar VARCHAR(12),
    IN p_doctor_id INT,
    IN p_symptoms TEXT,
    IN p_diagnosis TEXT,
    IN p_treatment TEXT,
    IN p_lab_tests VARCHAR(255)
)
BEGIN
    DECLARE new_visit_id INT;
    
    START TRANSACTION;
    
    -- Insert doctor visit
    INSERT INTO Doctor_Visit (
        Aadhar_number, Visit_Date, Visit_Reason,
        Doctor_ID, Diagnosis, Treatment_Plan
    )
    VALUES (
        p_aadhar, CURDATE(), p_symptoms,
        p_doctor_id, p_diagnosis, p_treatment
    );
    
    SET new_visit_id = LAST_INSERT_ID();
    
    -- Insert lab tests if provided
    IF p_lab_tests IS NOT NULL AND p_lab_tests != '' THEN
        INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name)
        VALUES (new_visit_id, p_aadhar, p_lab_tests);
    END IF;
    
    COMMIT;
END //
DELIMITER ;

-- Trigger for auditing personal information changes
DELIMITER //
CREATE TRIGGER personal_info_audit_trigger
AFTER UPDATE ON Personal_Information
FOR EACH ROW
BEGIN
    IF NEW.Name != OLD.Name THEN
        INSERT INTO Personal_Information_Audit 
        (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Name', OLD.Name, NEW.Name, CURRENT_USER());
    END IF;
    
    IF NEW.Phone_Number != OLD.Phone_Number THEN
        INSERT INTO Personal_Information_Audit 
        (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Phone_Number', OLD.Phone_Number, NEW.Phone_Number, CURRENT_USER());
    END IF;
    
    IF NEW.Email != OLD.Email THEN
        INSERT INTO Personal_Information_Audit 
        (Aadhar_number, Changed_Column, Old_Value, New_Value, Changed_By)
        VALUES (NEW.Aadhar_number, 'Email', OLD.Email, NEW.Email, CURRENT_USER());
    END IF;
END //
DELIMITER ;

-- Function to get patient full history
DELIMITER //
CREATE FUNCTION get_patient_visit_count(p_aadhar VARCHAR(12))
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE visit_count INT;
    
    SELECT COUNT(*) INTO visit_count
    FROM Doctor_Visit
    WHERE Aadhar_number = p_aadhar;
    
    RETURN visit_count;
END //
DELIMITER ;

-- Procedure to get patient summary
DELIMITER //
CREATE PROCEDURE get_patient_summary(IN p_aadhar VARCHAR(12))
BEGIN
    SELECT 
        pi.Name,
        calculate_age(pi.Date_of_Birth) as Age,
        pi.Gender,
        vs.Blood_Pressure,
        vs.Heart_Rate,
        vs.Respiratory_Rate,
        vs.Body_Temperature,
        vs.Height,
        vs.Weight,
        vs.BMI,
        get_patient_visit_count(p_aadhar) as TotalVisits,
        lf.Smoking_Status,
        lf.Alcohol_Consumption
    FROM Personal_Information pi
    LEFT JOIN Vital_Signs vs ON pi.Aadhar_number = vs.Aadhar_number
    LEFT JOIN Lifestyle_Factors lf ON pi.Aadhar_number = lf.Aadhar_number
    WHERE pi.Aadhar_number = p_aadhar;
END //
DELIMITER ;

-- Trigger to validate vital signs
DELIMITER //
CREATE TRIGGER validate_vital_signs
BEFORE INSERT ON Vital_Signs
FOR EACH ROW
BEGIN
    IF NEW.Heart_Rate < 40 OR NEW.Heart_Rate > 200 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Heart rate must be between 40 and 200';
    END IF;
    
    IF NEW.Respiratory_Rate < 8 OR NEW.Respiratory_Rate > 40 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Respiratory rate must be between 8 and 40';
    END IF;
    
    IF NEW.Body_Temperature < 95 OR NEW.Body_Temperature > 105 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Body temperature must be between 95°F and 105°F';
    END IF;
END //
DELIMITER ;
