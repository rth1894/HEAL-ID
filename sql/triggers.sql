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
