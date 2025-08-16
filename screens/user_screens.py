from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Input, Label, DataTable
from database.connection import DatabaseConnection, db
import pymysql


cursor = db.cursor
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
