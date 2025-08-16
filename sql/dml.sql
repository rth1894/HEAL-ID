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
