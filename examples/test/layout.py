import pytermgui as ptg
import pymysql
from typing import List, Dict, Any

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

def create_aliases():
    ptg.tim.alias("app.text", "#cfc7b0")
    ptg.tim.alias("app.header", "bold @#8C6701 #d9d2bd")
    ptg.tim.alias("app.header.fill", "@#FCBA03")
    ptg.tim.alias("app.title", "bold #FCBA03")
    ptg.tim.alias("app.button.label", "bold @#4D4940 app.text")
    ptg.tim.alias("app.button.highlight", "inverse app.button.label")
    ptg.tim.alias("app.footer", "@#242321")

def configure_widgets():
    ptg.boxes.DOUBLE.set_chars_of(ptg.Window)
    ptg.boxes.ROUNDED.set_chars_of(ptg.Container)
    ptg.Button.styles.label = "app.button.label"
    ptg.Button.styles.highlight = "app.button.highlight"
    ptg.Slider.styles.filled__cursor = "#8C6701"
    ptg.Slider.styles.filled_selected = "#FCBA03"
    ptg.Label.styles.value = "app.text"
    ptg.Window.styles.border__corner = "#C2B280"
    ptg.Container.styles.border__corner = "#4D4940"
    ptg.Splitter.set_char("separator", "")

class HealthDatabaseApp:
    def __init__(self):
        self.manager = ptg.WindowManager()
        self.current_doctor_id = None
        self.setup_header_footer()

    def setup_header_footer(self):
        header = ptg.Window("[app.header] Health Database Management System ", box="EMPTY", is_persistant=True)
        header.styles.fill = "app.header.fill"
        self.manager.add(header)

        footer = ptg.Window(
            ptg.Button("Quit", lambda *_: self.confirm_quit()),
            box="EMPTY",
            is_persistant=True,
        )
        footer.styles.fill = "app.footer"
        self.manager.add(footer)

    def confirm_quit(self):
        modal = ptg.Window(
            "[app.title]Are you sure you want to quit?",
            "",
            ptg.Container(
                ptg.Splitter(
                    ptg.Button("Yes", lambda *_: self.manager.stop()),
                    ptg.Button("No", lambda *_: modal.close()),
                ),
            ),
        ).center()
        modal.select(1)
        self.manager.add(modal)

    def show_main_menu(self):
        main_menu = ptg.Window(
            "[app.title]Main Menu",
            "",
            ptg.Button("Doctor Sign In", lambda *_: self.show_doctor_signin()),
            ptg.Button("User Sign In (Not Implemented)", lambda *_: ptg.tim.print("[yellow]User sign-in not implemented yet.[/]")),
            ptg.Button("Exit", lambda *_: self.confirm_quit()),
        ).center()
        self.manager.add(main_menu)

    def show_doctor_signin(self):
        signin_window = ptg.Window(
            "[app.title]Doctor Sign In",
            "",
            ptg.InputField(prompt="Doctor ID: ", prompt_style="bold"),
            ptg.Button("Sign In", lambda *_: self.process_doctor_signin(signin_window)),
            ptg.Button("Back", lambda *_: self.manager.remove(signin_window)),
        ).center()
        self.manager.add(signin_window)

    def process_doctor_signin(self, signin_window):
        doctor_id = signin_window.set_widgets(2).value
        if doctor_id in valid_doctor_ids:
            self.current_doctor_id = int(doctor_id)
            self.manager.remove(signin_window)
            self.show_doctor_menu()
        else:
            ptg.tim.print("[red]Invalid Doctor ID. Please try again.[/]")

    def show_doctor_menu(self):
        cursor.execute("SELECT Doctor_Name, Specialization FROM Doctors WHERE Doctor_ID = %s", (self.current_doctor_id,))
        result = cursor.fetchone()
        if result:
            name, specialization = result
            doctor_menu = ptg.Window(
                f"[app.title]Welcome, Dr. {name}",
                f"Specialization: {specialization}",
                f"ID: {self.current_doctor_id}",
                "",
                ptg.Button("New Consultation", lambda *_: self.show_consultation_form()),
                ptg.Button("View Patient History", lambda *_: self.show_patient_history_search()),
                ptg.Button("Sign Out", lambda *_: self.doctor_signout(doctor_menu)),
            ).center()
            self.manager.add(doctor_menu)

    def doctor_signout(self, doctor_menu):
        self.current_doctor_id = None
        self.manager.remove(doctor_menu)
        self.show_main_menu()

    def show_consultation_form(self):
        consultation_form = ptg.Window(
            "[app.title]New Consultation",
            "",
            ptg.InputField("Aadhar Number: ", prompt_style="bold"),
            ptg.Button("Fetch Patient Info", lambda *_: self.fetch_patient_info(consultation_form)),
            "",
            ptg.Label("Patient Information:"),
            ptg.Label("Name: "),
            ptg.Label("Age: "),
            ptg.Label("Gender: "),
            "",
            ptg.Label("Vital Signs:"),
            ptg.Label("Blood Pressure: "),
            ptg.Label("Heart Rate: "),
            ptg.Label("Respiratory Rate: "),
            ptg.Label("Body Temperature: "),
            ptg.Label("Height: "),
            ptg.Label("Weight: "),
            ptg.Label("BMI: "),
            "",
            ptg.Label("Consultation Details:"),
            ptg.InputField("Symptoms: ", prompt_style="bold"),
            ptg.InputField("Diagnosis: ", prompt_style="bold"),
            ptg.InputField("Treatment Plan: ", prompt_style="bold"),
            ptg.InputField("Lab Tests Required: ", prompt_style="bold"),
            ptg.InputField("Medications: ", prompt_style="bold"),
            ptg.InputField("Follow-up Date: ", prompt_style="bold"),
            ptg.InputField("Additional Notes: ", prompt_style="bold"),
            "",
            ptg.Button("Submit", lambda *_: self.submit_consultation(consultation_form)),
            ptg.Button("Back", lambda *_: self.manager.remove(consultation_form)),
        )
        self.manager.add(consultation_form)

    def fetch_patient_info(self, consultation_form):
        aadhar_number = consultation_form.get_widget(2).value
        cursor.execute("""
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
            consultation_form.get_widget(6).value = f"Name: {name}"
            consultation_form.get_widget(7).value = f"Age: {age}"
            consultation_form.get_widget(8).value = f"Gender: {gender}"
            consultation_form.get_widget(11).value = f"Blood Pressure: {bp}"
            consultation_form.get_widget(12).value = f"Heart Rate: {hr}"
            consultation_form.get_widget(13).value = f"Respiratory Rate: {rr}"
            consultation_form.get_widget(14).value = f"Body Temperature: {temp}"
            consultation_form.get_widget(15).value = f"Height: {height}"
            consultation_form.get_widget(16).value = f"Weight: {weight}"
            consultation_form.get_widget(17).value = f"BMI: {bmi}"
        else:
            ptg.tim.print("[red]Patient not found.[/]")

    def submit_consultation(self, consultation_form):
        aadhar_number = consultation_form.get_widget(2).value
        symptoms = consultation_form.get_widget(20).value
        diagnosis = consultation_form.get_widget(21).value
        treatment_plan = consultation_form.get_widget(22).value
        lab_tests = consultation_form.get_widget(23).value
        medications = consultation_form.get_widget(24).value
        follow_up_date = consultation_form.get_widget(25).value
        additional_notes = consultation_form.get_widget(26).value

        try:
            cursor.execute("""
                INSERT INTO Doctor_Visit 
                (Aadhar_number, Visit_Date, Visit_Reason, Doctor_ID, Diagnosis, Treatment_Plan)
                VALUES (%s, CURDATE(), %s, %s, %s, %s)
            """, (aadhar_number, symptoms, self.current_doctor_id, diagnosis, treatment_plan))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            visiting_id = cursor.fetchone()[0]

            if lab_tests:
                cursor.execute("""
                    INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name)
                    VALUES (%s, %s, %s)
                """, (visiting_id, aadhar_number, lab_tests))

            db.commit()
            ptg.tim.print("[green]Consultation submitted successfully![/]")
            self.manager.remove(consultation_form)
            self.show_doctor_menu()
        except pymysql.Error as e:
            db.rollback()
            ptg.tim.print(f"[red]An error occurred: {e}[/]")

    def show_patient_history_search(self):
        search_window = ptg.Window(
            "[app.title]Patient History Search",
            "",
            ptg.InputField("Aadhar Number: ", prompt_style="bold"),
            ptg.Button("Search", lambda *_: self.search_patient_history(search_window)),
            ptg.Button("Back", lambda *_: self.manager.remove(search_window)),
        ).center()
        self.manager.add(search_window)

    def search_patient_history(self, search_window):
        aadhar_number = search_window.get_widget(2).value
        cursor.execute("""
            SELECT dv.Visit_Date, d.Doctor_Name, dv.Diagnosis, dv.Treatment_Plan
            FROM Doctor_Visit dv
            JOIN Doctors d ON dv.Doctor_ID = d.Doctor_ID
            WHERE dv.Aadhar_number = %s
            ORDER BY dv.Visit_Date DESC
        """, (aadhar_number,))
        results = cursor.fetchall()

        if results:
            history_window = ptg.Window(
                f"[app.title]Patient History for Aadhar: {aadhar_number}",
                "",
                *[f"Date: {visit[0]}, Doctor: {visit[1]}, Diagnosis: {visit[2]}, Treatment: {visit[3]}" for visit in results],
                "",
                ptg.Button("Back", lambda *_: self.manager.remove(history_window)),
            )
            self.manager.add(history_window)
            self.manager.remove(search_window)
        else:
            ptg.tim.print("[yellow]No history found for this patient.[/]")

    def run(self):
        with self.manager as manager:
            self.show_main_menu()
            manager.run()

if __name__ == "__main__":
    create_aliases()
    configure_widgets()
    app = HealthDatabaseApp()
    app.run()
