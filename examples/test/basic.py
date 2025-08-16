import pytermgui as ptg
import pymysql

# MySQL connection 
db = pymysql.connect(
    host="localhost",
    user="python",
    password="Password@123",
    database="heal_id"
)
cursor = db.cursor()

def main_menu():
    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "HEAL-ID System",
                ptg.Button("Sign in as User", lambda *_: user_signin(manager)),
                ptg.Button("Sign in as Doctor", lambda *_: doctor_signin(manager)),
                ptg.Button("Exit", lambda *_: manager.stop()),
            )
            .set_title("Main Menu")
            .center()
        )
        manager.add(window)
        manager.run()

def user_signin(manager):
    aadhar_input = ptg.InputField("Aadhar Number: ")
    
    def validate_user():
        aadhar_number = aadhar_input.value
        cursor.execute("SELECT COUNT(*) FROM Personal_Information WHERE Aadhar_number = %s", (aadhar_number,))
        if cursor.fetchone()[0] > 0:
            manager.remove(signin_window)
            user_menu(manager, aadhar_number)
        else:
            error_label.value = "Invalid Aadhar Number"
    
    error_label = ptg.Label("", styles={'color': 'red'})
    
    signin_window = (
        ptg.Window(
            "User Sign In",
            aadhar_input,
            error_label,
            ptg.Button("Sign In", validate_user),
            ptg.Button("Back", lambda *_: manager.remove(signin_window)),
        )
        .set_title("User Sign In")
        .center()
    )
    manager.add(signin_window)

def user_menu(manager, aadhar_number):
    menu_window = (
        ptg.Window(
            f"Welcome, User {aadhar_number}",
            ptg.Button("View Health Records", lambda *_: view_health_records(manager, aadhar_number)),
            ptg.Button("View Visit History", lambda *_: view_visit_history(manager, aadhar_number)),
            ptg.Button("Back to Main Menu", lambda *_: manager.remove(menu_window)),
        )
        .set_title("User Menu")
        .center()
    )
    manager.add(menu_window)

def view_health_records(manager, aadhar_number):
    cursor.execute("""
        SELECT pi.Name, pi.Date_of_Birth, pi.Gender, vs.Blood_Pressure, vs.Heart_Rate, vs.BMI
        FROM Personal_Information pi
        LEFT JOIN Vital_Signs vs ON pi.Aadhar_number = vs.Aadhar_number
        WHERE pi.Aadhar_number = %s
    """, (aadhar_number,))
    record = cursor.fetchone()
    
    if record:
        records_window = (
            ptg.Window(
                f"Health Records for {aadhar_number}",
                ptg.Label(f"Name: {record[0]}"),
                ptg.Label(f"Date of Birth: {record[1]}"),
                ptg.Label(f"Gender: {record[2]}"),
                ptg.Label(f"Blood Pressure: {record[3]}"),
                ptg.Label(f"Heart Rate: {record[4]}"),
                ptg.Label(f"BMI: {record[5]}"),
                ptg.Button("Back", lambda *_: manager.remove(records_window)),
            )
            .set_title("Health Records")
            .center()
        )
        manager.add(records_window)
    else:
        error_window = (
            ptg.Window(
                "Error",
                ptg.Label("No health records found for this Aadhar number."),
                ptg.Button("Back", lambda *_: manager.remove(error_window)),
            )
            .center()
        )
        manager.add(error_window)

def view_visit_history(manager, aadhar_number):
    cursor.execute("""
        SELECT Visit_Date, Reason_for_Visit, Diagnosis
        FROM Doctor_Visit
        WHERE Aadhar_number = %s
        ORDER BY Visit_Date DESC
        LIMIT 5
    """, (aadhar_number,))
    visits = cursor.fetchall()
    
    visit_labels = [ptg.Label(f"Date: {visit[0]}, Reason: {visit[1]}, Diagnosis: {visit[2]}") for visit in visits]
    
    history_window = (
        ptg.Window(
            f"Visit History for {aadhar_number}",
            *visit_labels,
            ptg.Button("Back", lambda *_: manager.remove(history_window)),
        )
        .set_title("Visit History")
        .center()
    )
    manager.add(history_window)

def doctor_signin(manager):
    doctor_id_input = ptg.InputField("Doctor ID: ")
    
    def validate_doctor():
        doctor_id = doctor_id_input.value
        cursor.execute("SELECT COUNT(*) FROM Doctors WHERE Doctor_ID = %s", (doctor_id,))
        if cursor.fetchone()[0] > 0:
            manager.remove(signin_window)
            doctor_menu(manager, doctor_id)
        else:
            error_label.value = "Invalid Doctor ID"
    
    error_label = ptg.Label("", styles={'color': 'red'})
    
    signin_window = (
        ptg.Window(
            "Doctor Sign In",
            doctor_id_input,
            error_label,
            ptg.Button("Sign In", validate_doctor),
            ptg.Button("Back", lambda *_: manager.remove(signin_window)),
        )
        .set_title("Doctor Sign In")
        .center()
    )
    manager.add(signin_window)

def doctor_menu(manager, doctor_id):
    menu_window = (
        ptg.Window(
            f"Welcome, Doctor {doctor_id}",
            ptg.Button("New Patient Visit", lambda *_: new_patient_visit(manager, doctor_id)),
            ptg.Button("View Patient History", lambda *_: view_patient_history_prompt(manager)),
            ptg.Button("Back to Main Menu", lambda *_: manager.remove(menu_window)),
        )
        .set_title("Doctor Menu")
        .center()
    )
    manager.add(menu_window)

def new_patient_visit(manager, doctor_id):
    aadhar_input = ptg.InputField("Patient Aadhar Number: ")
    reason_input = ptg.InputField("Reason for Visit: ")
    diagnosis_input = ptg.InputField("Diagnosis: ")
    treatment_input = ptg.InputField("Treatment Plan: ")
    
    def submit_visit():
        aadhar_number = aadhar_input.value
        reason = reason_input.value
        diagnosis = diagnosis_input.value
        treatment = treatment_input.value
        
        cursor.execute("""
            INSERT INTO Doctor_Visit (Aadhar_number, Doctor_ID, Visit_Date, Reason_for_Visit, Diagnosis, Treatment_Plan)
            VALUES (%s, %s, CURDATE(), %s, %s, %s)
        """, (aadhar_number, doctor_id, reason, diagnosis, treatment))
        db.commit()
        
        manager.remove(visit_window)
    
    visit_window = (
        ptg.Window(
            "New Patient Visit",
            aadhar_input,
            reason_input,
            diagnosis_input,
            treatment_input,
            ptg.Button("Submit", submit_visit),
            ptg.Button("Back", lambda *_: manager.remove(visit_window)),
        )
        .set_title("New Patient Visit")
        .center()
    )
    manager.add(visit_window)

def view_patient_history_prompt(manager):
    aadhar_input = ptg.InputField("Patient Aadhar Number: ")
    
    def fetch_history():
        aadhar_number = aadhar_input.value
        cursor.execute("SELECT COUNT(*) FROM Personal_Information WHERE Aadhar_number = %s", (aadhar_number,))
        if cursor.fetchone()[0] > 0:
            view_patient_history(manager, aadhar_number)
        else:
            error_label.value = "Invalid Aadhar number"
    
    error_label = ptg.Label("", styles={'color': 'red'})
    
    prompt_window = (
        ptg.Window(
            "View Patient History",
            aadhar_input,
            error_label,
            ptg.Button("Fetch History", fetch_history),
            ptg.Button("Back", lambda *_: manager.remove(prompt_window)),
        )
        .set_title("Patient History")
        .center()
    )
    manager.add(prompt_window)

def view_patient_history(manager, aadhar_number):
    cursor.execute("""
        SELECT dv.Visit_Date, d.Name, dv.Reason_for_Visit, dv.Diagnosis, dv.Treatment_Plan
        FROM Doctor_Visit dv
        JOIN Doctors d ON dv.Doctor_ID = d.Doctor_ID
        WHERE dv.Aadhar_number = %s
        ORDER BY dv.Visit_Date DESC
    """, (aadhar_number,))
    visits = cursor.fetchall()
    
    visit_labels = [ptg.Label(f"Date: {visit[0]}, Doctor: {visit[1]}, Reason: {visit[2]}, Diagnosis: {visit[3]}") for visit in visits]
    
    history_window = (
        ptg.Window(
            f"Patient History for Aadhar: {aadhar_number}",
            *visit_labels,
            ptg.Button("Back", lambda *_: manager.remove(history_window)),
        )
        .set_title("Patient History")
        .center()
    )
    manager.add(history_window)

if __name__ == "__main__":
    main_menu()
