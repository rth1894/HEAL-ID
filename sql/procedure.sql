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
