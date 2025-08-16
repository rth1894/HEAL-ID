DELIMITER //

-- Get Doctor Name
CREATE PROCEDURE get_doctor_name(IN p_doctor_id INT, OUT p_doctor_name VARCHAR(100))
BEGIN
    SELECT Doctor_Name INTO p_doctor_name
    FROM Doctors
    WHERE Doctor_ID = p_doctor_id;
END //

-- Get Patient Info
CREATE PROCEDURE get_patient_info(IN p_aadhar_number VARCHAR(12))
BEGIN
    SELECT pi.Name, 
           TIMESTAMPDIFF(YEAR, pi.Date_of_Birth, CURDATE()) AS Age, 
           pi.Gender,
           vs.Blood_Pressure, 
           vs.Heart_Rate, 
           vs.Respiratory_Rate, 
           vs.Body_Temperature,
           vs.Height, 
           vs.Weight, 
           vs.BMI
    FROM Personal_Information pi
    LEFT JOIN Vital_Signs vs ON pi.Aadhar_number = vs.Aadhar_number
    WHERE pi.Aadhar_number = p_aadhar_number;
END //

-- Submit Consultation
CREATE PROCEDURE submit_consultation(
    IN p_aadhar_number VARCHAR(12),
    IN p_visit_date DATE,
    IN p_visit_reason TEXT,
    IN p_doctor_id INT,
    IN p_diagnosis TEXT,
    IN p_treatment_plan TEXT,
    OUT p_visiting_id INT
)
BEGIN
    INSERT INTO Doctor_Visit 
    (Aadhar_number, Visit_Date, Visit_Reason, Doctor_ID, Diagnosis, Treatment_Plan)
    VALUES (p_aadhar_number, p_visit_date, p_visit_reason, p_doctor_id, p_diagnosis, p_treatment_plan);
    
    SET p_visiting_id = LAST_INSERT_ID();
END //

-- Insert Lab Results
CREATE PROCEDURE insert_lab_results(
    IN p_visiting_id INT,
    IN p_aadhar_number VARCHAR(12),
    IN p_test_name TEXT
)
BEGIN
    INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name)
    VALUES (p_visiting_id, p_aadhar_number, p_test_name);
END //

-- Get Patient History
CREATE PROCEDURE get_patient_history(IN p_aadhar_number VARCHAR(12))
BEGIN
    SELECT dv.Visit_Date, d.Doctor_Name, dv.Diagnosis, dv.Treatment_Plan
    FROM Doctor_Visit dv
    JOIN Doctors d ON dv.Doctor_ID = d.Doctor_ID
    WHERE dv.Aadhar_number = p_aadhar_number
    ORDER BY dv.Visit_Date DESC;
END //

DELIMITER ;
