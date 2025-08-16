from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Input, Label, DataTable
from database.connection import DatabaseConnection, db

import pymysql
from datetime import datetime

cursor = db.cursor
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
        #db.cursor.callproc('get_doctor_name ', (self.doctor_id, ))
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
                Input(placeholder="Enter symptoms", id="symptoms"),
                Label("Diagnosis:"),
                Input(placeholder="Enter diagnosis", id="diagnosis"),
                Label("Treatment Plan:"),
                Input(placeholder="Enter treatment plan", id="treatment"),
                Label("Lab Tests Required:"),
                Input(placeholder="Enter required lab tests", id="lab_tests"),
                Label("Medications:"),
                Input(placeholder="Enter medications", id="medications"),
                Label("Follow-up Date:"),
                Input(placeholder="Enter follow-up date", id="followup"),
                Label("Additional Notes:"),
                Input(placeholder="Enter additional notes", id="notes"),
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
        db.cursor.callproc('get_patient_info', (aadhar_number,))
        """
        cursor.execute("""
        """
            SELECT pi.Name, TIMESTAMPDIFF(YEAR, pi.Date_of_Birth, CURDATE()) AS Age, pi.Gender,
                   vs.Blood_Pressure, vs.Heart_Rate, vs.Respiratory_Rate, vs.Body_Temperature,
                   vs.Height, vs.Weight, vs.BMI
            FROM Personal_Information pi
            LEFT JOIN Vital_Signs vs ON pi.Aadhar_number = vs.Aadhar_number
            WHERE pi.Aadhar_number = %s
            """
        """, (aadhar_number,))
        """
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
            symptoms = self.query_one("#symptoms").value
            diagnosis = self.query_one("#diagnosis").value
            treatment_plan = self.query_one("#treatment").value
            lab_tests = self.query_one("#lab_tests").value
            medications = self.query_one("#medications").value
            follow_up_date = self.query_one("#followup").value
            additional_notes = self.query_one("#notes").value

            #db.cursor.callproc('submit_consultation', (aadhar_number, datetime.now().strftime("%Y-%m-%d"), symptoms, self.doctor_id, diagnosis, treatment_plan,''))

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
        yield ScrollableContainer(DataTable(id="history_table"))
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

        table = self.query_one("#history_table")
        table.add_columns("Visit Date", "Doctor", "Diagnosis", "Treatment Plan")

        if results:
            for visit in results:
                table.add_row(*visit)
        else:
            table.add_row("No history found", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()
