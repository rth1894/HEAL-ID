import pytermgui as ptg
import pymysql

# Database connection
db = pymysql.connect(
    host="localhost",
    user="python",
    password="Password@123",
    database="heal_id"
)
cursor = db.cursor()

def get_valid_doctor_ids():
    cursor.execute("SELECT Doctor_ID FROM Doctors")
    return [str(row[0]) for row in cursor.fetchall()]

valid_doctor_ids = get_valid_doctor_ids()

def main_menu():
    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "Heal - ID",
                "Sign in As",
                ptg.Button("User", lambda *_: user_signin()),
                ptg.Button("Doctor", lambda *_: doctor_signin(manager)),
                ptg.Button("Exit", lambda *_: manager.stop()),
            )
            .set_title("Main Menu")
            .center()
        )
        manager.add(window)

def user_signin():
    ptg.tim.print("[red]User sign-in not implemented yet.[/]")

def doctor_signin(manager):
    id_input = ptg.InputField(prompt="Enter your ID: ")
    id_input.prompt_style = ptg.tim.parse("[bold]")

    def submit_id(*_):
        value = id_input.value
        if value in valid_doctor_ids:
            show_doctor_form(manager, int(value))
        else:
            ptg.tim.print("[red]Invalid Doctor ID. Please try again.[/]")

    signin_window = (
        ptg.Window(
            "Doctor Sign-in",
            "",
            id_input,
            ptg.Button("Submit", submit_id),
            ptg.Button("Back", lambda *_: manager.remove(signin_window)),
        )
        .set_title("Doctor Sign-in")
        .center()
    )
    manager.add(signin_window)

def show_doctor_form(manager, doctor_id):
    cursor.execute("SELECT Doctor_Name, Specialization FROM Doctors WHERE Doctor_ID = %s", (doctor_id,))
    result = cursor.fetchone()
    if result:
        name, specialization = result
        form_window = (
            ptg.Window(
                f"Welcome, {name}",
                f"Specialization: {specialization}",
                "",
                ptg.Button("Start Consultation", lambda *_: start_consultation(manager, doctor_id)),
                ptg.Button("Back", lambda *_: manager.remove(form_window)),
            )
            .set_title("Doctor Form")
            .center()
        )
        manager.add(form_window)
    else:
        ptg.tim.print("[red]Doctor not found.[/]")

def start_consultation(manager, doctor_id):

    consultation = ["Symptoms: ","Diagnosis: ","Treatment Plan: ","Lab Tests Required: ","Medications: ","Follow-up Date: ","Additional Notes: "]
    lengt = []


    content = [
        ptg.InputField("Aadhar Number: ", prompt_style="bold"),
        ptg.Label(""),  # Spacer
        ptg.Label("Patient Information:"),
        ptg.Label("Name: "),
        ptg.Label("Age: "),
        ptg.Label("Gender: "),
        ptg.Label("Blood Pressure: "),
        ptg.Label("Heart Rate: "),
        ptg.Label("Respiratory Rate: "),
        ptg.Label("Body Temperature: "),
        ptg.Label("Height: "),
        ptg.Label("Weight: "),
        ptg.Label("BMI: "),
        ptg.Label(""),  # Spacer
        ptg.Label("Consultation Details:"),
        ptg.InputField(consultation[0], prompt_style="bold"),
        ptg.InputField(consultation[1], prompt_style="bold"),
        ptg.InputField(consultation[2], prompt_style="bold"),
        ptg.InputField(consultation[3], prompt_style="bold"),
        ptg.InputField(consultation[4], prompt_style="bold"),
        ptg.InputField(consultation[5], prompt_style="bold"),
        ptg.InputField(consultation[6], prompt_style="bold"),
    ]


    scroll_pos = [0]  # Use a list to store the scroll position so it can be modified in nested functions
    visible_items = 25  # Adjust this value based on your terminal size

    def scroll_up(*_):
        if scroll_pos[0] > 0:
            scroll_pos[0] -= 1
            update_window()

    def scroll_down(*_):
        if scroll_pos[0] < len(content) - visible_items:
            scroll_pos[0] += 1
            update_window()

    def fetch_patient_info_and_update(*_):
        fetch_patient_info(content, update_window)

    def update_window():
        visible_content = content[scroll_pos[0]:scroll_pos[0] + visible_items]
        consultation_window.body = [
            *visible_content,
            ptg.Button("Fetch Patient Info", fetch_patient_info_and_update),
            ptg.Button("↑ Scroll Up", scroll_up),
            ptg.Button("↓ Scroll Down", scroll_down),
            ptg.Button("Submit", lambda *_: submit_consultation(manager, consultation_window, doctor_id, content)),
            ptg.Button("Back", lambda *_: manager.remove(consultation_window)),
        ]

    consultation_window = (
        ptg.Window(
            "New Consultation",
            *content[:visible_items],
            ptg.Button("Fetch Patient Info", fetch_patient_info_and_update),
            ptg.Button("↑ Scroll Up", scroll_up),
            ptg.Button("↓ Scroll Down", scroll_down),
            ptg.Button("Submit", lambda *_: submit_consultation(manager, consultation_window, doctor_id, content)),
            ptg.Button("Back", lambda *_: manager.remove(consultation_window)),
        )
        .set_title("Consultation Form")
        .center()
    )
    manager.add(consultation_window)

def fetch_patient_info(content, update_window):
    aadhar_number = content[0].value[15:]
    cursor.execute(f"""
        SELECT pi.Name, TIMESTAMPDIFF(YEAR, pi.Date_of_Birth, CURDATE()) AS Age, pi.Gender,
               vs.Blood_Pressure, vs.Heart_Rate, vs.Respiratory_Rate, vs.Body_Temperature,
               vs.Height, vs.Weight, vs.BMI
        FROM Personal_Information pi
        LEFT JOIN Vital_Signs vs ON pi.Aadhar_number = vs.Aadhar_number
        WHERE pi.Aadhar_number = %s
    """, (aadhar_number,))
    result = cursor.fetchone()
    
    if result:
        name, age, gender, bp, hr, rr, temp, height, weight, bmi = result
        content[3].value = f"Name: {name}"
        content[4].value = f"Age: {age}"
        content[5].value = f"Gender: {gender}"
        content[6].value = f"Blood Pressure: {bp}"
        content[7].value = f"Heart Rate: {hr}"
        content[8].value = f"Respiratory Rate: {rr}"
        content[9].value = f"Body Temperature: {temp}"
        content[10].value = f"Height: {height}"
        content[11].value = f"Weight: {weight}"
        content[12].value = f"BMI: {bmi}"
        update_window()
    else:
        ptg.tim.print("[red]Patient not found.[/]")

def length_of_var(var):
    a = var.index(":")
    var = var[a+2:]
    return var

def submit_consultation(manager, window, doctor_id, content):
    aadhar_number = content[0].value
    aadhar_number = aadhar_number[15:]
    symptoms = length_of_var(content[15].value)
    diagnosis = length_of_var(content[16].value)
    treatment_plan = length_of_var(content[17].value)
    lab_tests =length_of_var( content[18].value)
    medications =length_of_var( content[19].value)
    follow_up_date =length_of_var( content[20].value)
    additional_notes = length_of_var(content[21].value)

    try:
        cursor.execute("""
            INSERT INTO Doctor_Visit 
            (Aadhar_number, Visit_Date, Visit_Reason, Doctor_ID, Diagnosis, Treatment_Plan)
            VALUES (%s, CURDATE(), %s, %s, %s, %s)
        """, (aadhar_number, symptoms, doctor_id, diagnosis, treatment_plan))
        
        cursor.execute("select Visiting_id from Doctor_Visit order by Visiting_id DESC limit 1;")

        visiting_id = cursor.fetchone()
        print(visiting_id)

        if lab_tests:
            cursor.execute("""
                INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name)
                VALUES (%s, %s, %s)
            """, (visiting_id, aadhar_number, lab_tests))

        # Commit the transaction
        db.commit()
        ptg.tim.print("[green]Consultation submitted successfully![/]")
        manager.remove(window)
    except pymysql.Error as e:
        db.rollback()
        ptg.tim.print(f"[red]An error occurred: {e}[/]")

if __name__ == "__main__":
    main_menu()
