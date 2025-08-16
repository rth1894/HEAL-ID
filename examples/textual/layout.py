from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Header, Footer, Input, Static, Label, TextArea
from textual.screen import Screen
from textual import events
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

class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("HEAL-ID Main Menu", classes="title"),
            Button("Doctor Sign In", id="doctor_signin"),
            Button("User Sign In", id="user_signin", disabled=True),
            Button("Exit", id="exit"),
            id="menu"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "doctor_signin":
            self.app.push_screen(DoctorSignIn())
        elif event.button.id == "exit":
            self.app.exit()

class DoctorSignIn(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("HEAL-ID Doctor Sign In", classes="title"),
            Input(placeholder="Enter Doctor ID", id="doctor_id"),
            Button("Sign In", id="signin"),
            Button("Back", id="back"),
            id="signin_form"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "signin":
            doctor_id = self.query_one("#doctor_id").value
            if doctor_id in valid_doctor_ids:
                self.app.push_screen(DoctorMenu(doctor_id))
            else:
                self.notify("Invalid Doctor ID", severity="error")
        elif event.button.id == "back":
            self.app.pop_screen()

class DoctorMenu(Screen):
    def __init__(self, doctor_id: str):
        super().__init__()
        self.doctor_id = doctor_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Welcome to HEAL-ID, Dr. {self.get_doctor_name()}", classes="title"),
            Button("New Consultation", id="new_consultation"),
            Button("Sign Out", id="signout"),
            id="doctor_menu"
        )
        yield Footer()

    def get_doctor_name(self) -> str:
        cursor.execute("SELECT Doctor_Name FROM Doctors WHERE Doctor_ID = %s", (self.doctor_id,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "new_consultation":
            self.app.push_screen(ConsultationForm(self.doctor_id))
        elif event.button.id == "signout":
            self.app.pop_screen()

class ConsultationForm(Screen):
    def __init__(self, doctor_id: str):
        super().__init__()
        self.doctor_id = doctor_id

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Horizontal(
            ScrollableContainer(
                Static("HEAL-ID New Consultation", classes="title"),
                Input(placeholder="Aadhar Number", id="aadhar"),
                Button("Fetch Patient Info", id="fetch_info"),
                Static("Consultation Details:", classes="subtitle"),
                Label("Symptoms:"),
                TextArea(id="symptoms"),
                Label("Diagnosis:"),
                TextArea(id="diagnosis"),
                Label("Treatment Plan:"),
                TextArea(id="treatment"),
                Label("Lab Tests Required:"),
                TextArea(id="lab_tests"),
                Label("Medications:"),
                TextArea(id="medications"),
                Label("Follow-up Date:"),
                TextArea(id="followup"),
                Label("Additional Notes:"),
                TextArea(id="notes"),
                Button("Submit", id="submit"),
                Button("Back", id="back"),
                id="consultation_form"
            ),
            Vertical(
                Static("Patient Information", classes="subtitle"),
                Label("Name: ", id="name"),
                Label("Age: ", id="age"),
                Label("Gender: ", id="gender"),
                Static("Vital Signs:", classes="subtitle"),
                Label("Blood Pressure: ", id="bp"),
                Label("Heart Rate: ", id="hr"),
                Label("Respiratory Rate: ", id="rr"),
                Label("Body Temperature: ", id="temp"),
                Label("Height: ", id="height"),
                Label("Weight: ", id="weight"),
                Label("BMI: ", id="bmi"),
                Button("View Patient History", id="view_history"),
                id="patient_info_sidebar"
            ),
            id="consultation_layout"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "fetch_info":
            self.fetch_patient_info()
        elif event.button.id == "submit":
            self.submit_consultation()
        elif event.button.id == "back":
            self.app.pop_screen()
        elif event.button.id == "view_history":
            self.view_patient_history()

    def fetch_patient_info(self):
        aadhar_number = self.query_one("#aadhar").value
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
            self.query_one("#name").update(f"Name: {name}")
            self.query_one("#age").update(f"Age: {age}")
            self.query_one("#gender").update(f"Gender: {gender}")
            self.query_one("#bp").update(f"Blood Pressure: {bp}")
            self.query_one("#hr").update(f"Heart Rate: {hr}")
            self.query_one("#rr").update(f"Respiratory Rate: {rr}")
            self.query_one("#temp").update(f"Body Temperature: {temp}")
            self.query_one("#height").update(f"Height: {height}")
            self.query_one("#weight").update(f"Weight: {weight}")
            self.query_one("#bmi").update(f"BMI: {bmi}")
        else:
            self.notify("Patient not found", severity="warning")

    def submit_consultation(self):
        try:
            aadhar_number = self.query_one("#aadhar").value
            symptoms = self.query_one("#symptoms").text
            diagnosis = self.query_one("#diagnosis").text
            treatment_plan = self.query_one("#treatment").text
            lab_tests = self.query_one("#lab_tests").text
            medications = self.query_one("#medications").text
            follow_up_date = self.query_one("#followup").text
            additional_notes = self.query_one("#notes").text

            cursor.execute("""
                INSERT INTO Doctor_Visit 
                (Aadhar_number, Visit_Date, Visit_Reason, Doctor_ID, Diagnosis, Treatment_Plan)
                VALUES (%s, CURDATE(), %s, %s, %s, %s)
            """, (aadhar_number, symptoms, self.doctor_id, diagnosis, treatment_plan))
            
            cursor.execute("SELECT LAST_INSERT_ID()")
            visiting_id = cursor.fetchone()[0]

            if lab_tests:
                cursor.execute("""
                    INSERT INTO Laboratory_Results (Visiting_id, Aadhar_number, Test_Name)
                    VALUES (%s, %s, %s)
                """, (visiting_id, aadhar_number, lab_tests))

            db.commit()
            self.notify("Consultation submitted successfully", severity="success")
            self.app.pop_screen()
        except pymysql.Error as e:
            db.rollback()
            self.notify(f"An error occurred: {e}", severity="error")

    def view_patient_history(self):
        aadhar_number = self.query_one("#aadhar").value
        self.app.push_screen(PatientHistoryDisplay(aadhar_number))

class PatientHistoryDisplay(Screen):
    def __init__(self, aadhar_number: str):
        super().__init__()
        self.aadhar_number = aadhar_number

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(f"HEAL-ID Patient History for Aadhar: {self.aadhar_number}", classes="title")
        yield ScrollableContainer(id="history_display")
        yield Button("Back", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.fetch_patient_history()

    def fetch_patient_history(self):
        cursor.execute("""
            SELECT dv.Visit_Date, d.Doctor_Name, dv.Diagnosis, dv.Treatment_Plan
            FROM Doctor_Visit dv
            JOIN Doctors d ON dv.Doctor_ID = d.Doctor_ID
            WHERE dv.Aadhar_number = %s
            ORDER BY dv.Visit_Date DESC
        """, (self.aadhar_number,))
        results = cursor.fetchall()

        history_container = self.query_one("#history_display")
        if results:
            for visit in results:
                history_container.mount(Static(f"Date: {visit[0]}, Doctor: {visit[1]}, Diagnosis: {visit[2]}, Treatment: {visit[3]}"))
        else:
            history_container.mount(Static("No history found for this patient"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()

class HEALID_App(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #menu, #signin_form, #doctor_menu {
        width: 80%;
        height: auto;
        border: solid green;
        padding: 1 2;
    }

    #consultation_layout {
        width: 100%;
        height: 100%;
    }

    #consultation_form {
        width: 70%;
        height: 100%;
        border: solid green;
        padding: 1 2;
    }

    #patient_info_sidebar {
        width: 30%;
        height: 100%;
        border: solid green;
        padding: 1 2;
    }

    #history_display {
        width: 80%;
        height: 80%;
        border: solid green;
        padding: 1 2;
    }

    .title {
        content-align: center middle;
        width: 100%;
        height: 3;
        background: $boost;
        color: $text;
    }

    .subtitle {
        color: $text-muted;
        margin: 1 0;
    }

    Button {
        width: 100%;
    }

    Input, TextArea {
        width: 100%;
    }
    """

    def on_mount(self) -> None:
        self.push_screen(MainMenu())

if __name__ == "__main__":
    app = HEALID_App()
    app.run()
