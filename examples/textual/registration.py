from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Header, Footer, Input, Static, Label, TextArea, DataTable
from textual.screen import Screen
from textual import events
import pymysql
from typing import List, Dict, Any
from datetime import datetime

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

def get_valid_aadhar_numbers():
    cursor.execute("SELECT Aadhar_number FROM Personal_Information
    return [str(row[0]) for row in cursor.fetchall()]

valid_doctor_ids = get_valid_doctor_ids()
valid_aadhar_numbers = get_valid_aadhar_numbers()


class MainMenu(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Welcome to HEAL-ID", classes="title"),
            Button("Sign In", id="signin"),
            Button("Register", id="register"),
            Button("Exit", id="exit"),
            id="menu"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "signin":
            self.app.push_screen(SignInOptions())
        elif event.button.id == "register":
            self.app.push_screen(RegisterOptions())
        elif event.button.id == "exit":
            self.app.exit()

class SignInOptions(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Sign In Options", classes="title"),
            Button("Doctor Sign In", id="doctor_signin"),
            Button("User Sign In", id="user_signin"),
            Button("Back", id="back"),
            id="signin_options"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "doctor_signin":
            self.app.push_screen(DoctorSignIn())
        elif event.button.id == "user_signin":
            self.app.push_screen(UserSignIn())
        elif event.button.id == "back":
            self.app.pop_screen()

class RegisterOptions(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Register Options", classes="title"),
            Button("Register as Doctor", id="doctor_register"),
            Button("Register as User", id="user_register"),
            Button("Back", id="back"),
            id="register_options"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "doctor_register":
            self.app.push_screen(DoctorRegistration())
        elif event.button.id == "user_register":
            self.app.push_screen(UserRegistration())
        elif event.button.id == "back":
            self.app.pop_screen()

class UserRegistration(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("HEAL-ID User Registration", classes="title"),
            Label("Personal Information", classes="section-header"),
            Input(placeholder="Aadhar Number (12 digits)", id="aadhar"),
            Input(placeholder="Full Name", id="name"),
            Input(placeholder="Date of Birth (YYYY-MM-DD)", id="dob"),
            Input(placeholder="Gender (Male/Female/Other)", id="gender"),
            Input(placeholder="Phone Number", id="phone"),
            Input(placeholder="Email", id="email"),
            Label("Address Information", classes="section-header"),
            Input(placeholder="Street Address", id="street"),
            Input(placeholder="City", id="city"),
            Input(placeholder="State", id="state"),
            Input(placeholder="ZIP Code", id="zip"),
            Label("Emergency Contact", classes="section-header"),
            Input(placeholder="Emergency Contact Name", id="emergency_name"),
            Input(placeholder="Emergency Contact Phone", id="emergency_phone"),
            Horizontal(
                Button("Register", id="register"),
                Button("Back", id="back"),
            ),
            id="registration_form"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register":
            self.register_user()
        elif event.button.id == "back":
            self.app.pop_screen()

    def register_user(self):
        try:
            # Extract form data
            aadhar = self.query_one("#aadhar").value
            name = self.query_one("#name").value
            dob = self.query_one("#dob").value
            gender = self.query_one("#gender").value
            phone = self.query_one("#phone").value
            email = self.query_one("#email").value
            street = self.query_one("#street").value
            city = self.query_one("#city").value
            state = self.query_one("#state").value
            zip_code = self.query_one("#zip").value
            emergency_name = self.query_one("#emergency_name").value
            emergency_phone = self.query_one("#emergency_phone").value

            # Validate required fields
            if not all([aadhar, name, dob, gender, phone]):
                self.notify("Please fill all required fields", severity="error")
                return

            # Validate Aadhar number format
            if len(aadhar) != 12 or not aadhar.isdigit():
                self.notify("Invalid Aadhar number format", severity="error")
                return

            # Start transaction
            cursor.execute("START TRANSACTION")

            # Insert address first
            cursor.execute("""
                INSERT INTO Address (Street, City, State, Zip_Code)
                VALUES (%s, %s, %s, %s)
            """, (street, city, state, zip_code))
            
            address_id = cursor.lastrowid

            # Insert personal information
            cursor.execute("""
                INSERT INTO Personal_Information 
                (Aadhar_number, Name, Date_of_Birth, Gender, Phone_Number, 
                Email, Address_ID, Emergency_Contact_Name, Emergency_Contact_Phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (aadhar, name, dob, gender, phone, email, address_id, 
                  emergency_name, emergency_phone))

            # Initialize other related tables
            cursor.execute("""
                INSERT INTO Medical_History (Aadhar_number)
                VALUES (%s)
            """, (aadhar,))

            cursor.execute("""
                INSERT INTO Lifestyle_Factors 
                (Aadhar_number, Smoking_Status, Alcohol_Consumption)
                VALUES (%s, 'Non-smoker', 'None')
            """, (aadhar,))

            # Commit transaction
            db.commit()
            self.notify("Registration successful!", severity="success")
            valid_aadhar_numbers.append(aadhar)
            self.app.pop_screen()

        except pymysql.Error as e:
            db.rollback()
            self.notify(f"Registration failed: {str(e)}", severity="error")

class DoctorRegistration(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("HEAL-ID Doctor Registration", classes="title"),
            Input(placeholder="Full Name", id="name"),
            Input(placeholder="Specialization", id="specialization"),
            Horizontal(
                Button("Register", id="register"),
                Button("Back", id="back"),
            ),
            id="doctor_registration_form"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "register":
            self.register_doctor()
        elif event.button.id == "back":
            self.app.pop_screen()

    def register_doctor(self):
        try:
            name = self.query_one("#name").value
            specialization = self.query_one("#specialization").value

            if not all([name, specialization]):
                self.notify("Please fill all fields", severity="error")
                return

            cursor.execute("""
                INSERT INTO Doctors (Doctor_Name, Specialization)
                VALUES (%s, %s)
            """, (name, specialization))

            db.commit()
            doctor_id = cursor.lastrowid
            valid_doctor_ids.append(str(doctor_id))
            self.notify(f"Registration successful! Your Doctor ID is: {doctor_id}", severity="success")
            self.app.pop_screen()

        except pymysql.Error as e:
            db.rollback()
            self.notify(f"Registration failed: {str(e)}", severity="error")
class UserSignIn(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("HEAL-ID User Sign In", classes="title"),
            Input(placeholder="Enter Aadhar Number", id="aadhar_number"),
            Button("Sign In", id="signin"),
            Button("Back", id="back"),
            id="signin_form"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "signin":
            aadhar_number = self.query_one("#aadhar_number").value
            if aadhar_number in valid_aadhar_numbers:
                self.app.push_screen(UserMenu(aadhar_number))
            else:
                self.notify("Invalid Aadhar Number", severity="error")
        elif event.button.id == "back":
            self.app.pop_screen()

class UserMenu(Screen):
    def __init__(self, aadhar_number: str):
        super().__init__()
        self.aadhar_number = aadhar_number

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static(f"Welcome to HEAL-ID, {self.get_user_name()}", classes="title"),
            Button("Update Vital Signs", id="update_vitals"),
            Button("View Medical History", id="view_history"),
            Button("Sign Out", id="signout"),
            id="user_menu"
        )
        yield Footer()

    def get_user_name(self) -> str:
        cursor.execute("SELECT Name FROM Personal_Information WHERE Aadhar_number = %s", (self.aadhar_number,))
        result = cursor.fetchone()
        return result[0] if result else "Unknown"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "update_vitals":
            self.app.push_screen(UpdateVitalSigns(self.aadhar_number))
        elif event.button.id == "view_history":
            self.app.push_screen(UserHistoryDisplay(self.aadhar_number))
        elif event.button.id == "signout":
            self.app.pop_screen()

class UpdateVitalSigns(Screen):
    def __init__(self, aadhar_number: str):
        super().__init__()
        self.aadhar_number = aadhar_number

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Update Vital Signs", classes="title"),
            Label("Blood Pressure:"),
            Input(placeholder="e.g., 120/80", id="bp"),
            Label("Heart Rate:"),
            Input(placeholder="e.g., 72", id="hr"),
            Label("Respiratory Rate:"),
            Input(placeholder="e.g., 16", id="rr"),
            Label("Body Temperature:"),
            Input(placeholder="e.g., 98.6", id="temp"),
            Label("Height (cm):"),
            Input(placeholder="e.g., 170", id="height"),
            Label("Weight (kg):"),
            Input(placeholder="e.g., 70", id="weight"),
            Button("Submit", id="submit"),
            Button("Back", id="back"),
            id="vitals_form"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.load_current_vitals()

    def load_current_vitals(self):
        cursor.execute("""
            SELECT Blood_Pressure, Heart_Rate, Respiratory_Rate, 
                   Body_Temperature, Height, Weight, BMI
            FROM Vital_Signs
            WHERE Aadhar_number = %s
        """, (self.aadhar_number,))
        result = cursor.fetchone()
        
        if result:
            self.query_one("#bp").value = str(result[0] or '')
            self.query_one("#hr").value = str(result[1] or '')
            self.query_one("#rr").value = str(result[2] or '')
            self.query_one("#temp").value = str(result[3] or '')
            self.query_one("#height").value = str(result[4] or '')
            self.query_one("#weight").value = str(result[5] or '')

    def calculate_bmi(self, height_cm: float, weight_kg: float) -> float:
        height_m = height_cm / 100
        return round(weight_kg / (height_m * height_m), 2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            try:
                height = float(self.query_one("#height").value)
                weight = float(self.query_one("#weight").value)
                bmi = self.calculate_bmi(height, weight)

                cursor.execute("""
                    REPLACE INTO Vital_Signs 
                    (Aadhar_number, Blood_Pressure, Heart_Rate, Respiratory_Rate,
                     Body_Temperature, Height, Weight, BMI)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    self.aadhar_number,
                    self.query_one("#bp").value,
                    self.query_one("#hr").value,
                    self.query_one("#rr").value,
                    self.query_one("#temp").value,
                    height,
                    weight,
                    bmi
                ))
                db.commit()
                self.notify("Vital signs updated successfully", severity="success")
                self.app.pop_screen()
            except ValueError as e:
                self.notify("Please enter valid numbers", severity="error")
            except pymysql.Error as e:
                db.rollback()
                self.notify(f"An error occurred: {e}", severity="error")
        elif event.button.id == "back":
            self.app.pop_screen()

class UserHistoryDisplay(Screen):
    def __init__(self, aadhar_number: str):
        super().__init__()
        self.aadhar_number = aadhar_number

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield ScrollableContainer(
            Static("Medical History", classes="title"),
            DataTable(id="history_table"),
            Button("View Vital Signs History", id="view_vitals"),
            Button("Back", id="back"),
            id="history_display"
        )
        yield Footer()

    def on_mount(self) -> None:
        self.show_medical_history()

    def show_medical_history(self):
        cursor.execute("""
            SELECT dv.Visit_Date, d.Doctor_Name, dv.Visit_Reason, 
                   dv.Diagnosis, dv.Treatment_Plan
            FROM Doctor_Visit dv
            JOIN Doctors d ON dv.Doctor_ID = d.Doctor_ID
            WHERE dv.Aadhar_number = %s
            ORDER BY dv.Visit_Date DESC
        """, (self.aadhar_number,))
        results = cursor.fetchall()

        table = self.query_one("#history_table")
        table.add_columns("Date", "Doctor", "Reason", "Diagnosis", "Treatment")

        if results:
            for visit in results:
                table.add_row(*visit)
        else:
            table.add_row("No history found", "", "", "", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "view_vitals":
            self.app.push_screen(VitalSignsHistory(self.aadhar_number))
        elif event.button.id == "back":
            self.app.pop_screen()

class VitalSignsHistory(Screen):
    def __init__(self, aadhar_number: str):
        super().__init__()
        self.aadhar_number = aadhar_number

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Static("Vital Signs History", classes="title"),
            DataTable(id="vitals_table"),
            Button("Back", id="back"),
            id="vitals_history"
        )
        yield Footer()

    def on_mount(self) -> None:
        cursor.execute("""
            SELECT Blood_Pressure, Heart_Rate, Respiratory_Rate, 
                   Body_Temperature, Height, Weight, BMI
            FROM Vital_Signs
            WHERE Aadhar_number = %s
        """, (self.aadhar_number,))
        result = cursor.fetchone()

        table = self.query_one("#vitals_table")
        table.add_columns("Measurement", "Value")

        if result:
            measurements = [
                ("Blood Pressure", result[0]),
                ("Heart Rate", f"{result[1]} bpm"),
                ("Respiratory Rate", f"{result[2]} /min"),
                ("Body Temperature", f"{result[3]}°F"),
                ("Height", f"{result[4]} cm"),
                ("Weight", f"{result[5]} kg"),
                ("BMI", result[6])
            ]
            for measurement, value in measurements:
                table.add_row(measurement, str(value))
        else:
            table.add_row("No vital signs recorded", "")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.app.pop_screen()


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
            symptoms = self.query_one("#symptoms").value
            diagnosis = self.query_one("#diagnosis").value
            treatment_plan = self.query_one("#treatment").value
            lab_tests = self.query_one("#lab_tests").value
            medications = self.query_one("#medications").value
            follow_up_date = self.query_one("#followup").value
            additional_notes = self.query_one("#notes").value

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
class HEALID_App(App):
    CSS = """
    Screen {
        align: center middle;
    }

    #menu, #signin_form, #doctor_menu, #registration_form, #doctor_registration_form {
        width: 80%;
        height: auto;
        border: solid red;
        padding: 1 2;
    }

    .section-header {
        background: $boost;
        color: $text;
        padding: 1 1;
        margin: 1 0;
        width: 100%;
    }
    #consultation_layout {
        width: 100%;
        height: 100%;
    }

    #consultation_form {
        width: 70%;
        height: 100%;
        border: solid red;
        padding: 1 2;
    }

    #patient_info_sidebar {
        width: 30%;
        height: 100%;
        border: solid red;
        padding: 1 2;
    }

    #history_display {
        width: 80%;
        height: 80%;
        border: solid red;
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
    Input {
        width: 100%;
    }

    #consultation_form {
        width: 70%;
        height: 100%;
        border: solid red;
        padding: 1 2;
        overflow-y: auto;
    }

    #history_table {
        height: 100%;
        border: solid red;
    }

    DataTable > .datatable--header {
        background: $accent;
        color: $text;
    }

    DataTable > .datatable--body {
        height: 1fr;
    }

    .datatable--row {
        height: auto;
    }

    .datatable--row-cell {
        content-align: left middle;
        padding: 0 1;
        height: auto;
    }
"""

    def on_mount(self) -> None:
        self.push_screen(MainMenu())

if __name__ == "__main__":
    app = HEALID_App()
    app.run()
