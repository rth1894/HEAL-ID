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
