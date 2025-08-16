from textual.app import ComposeResult
from textual.containers import Container, ScrollableContainer, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Input, Label
from database.connection import DatabaseConnection, db
import pymysql
from datetime import datetime

cursor = db.cursor

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
            db.valid_aadhar_numbers.append(aadhar)
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
            db.valid_doctor_ids.append(str(doctor_id))
            self.notify(f"Registration successful! Your Doctor ID is: {doctor_id}", severity="success")
            self.app.pop_screen()

        except pymysql.Error as e:
            db.rollback()
            self.notify(f"Registration failed: {str(e)}", severity="error")
