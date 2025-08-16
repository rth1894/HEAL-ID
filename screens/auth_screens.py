from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static, Input
from .user_screens import UserMenu
from .doctor_screens import DoctorMenu
from .registration_screens import UserRegistration, DoctorRegistration
from database.connection import DatabaseConnection, db
#from database.connection import db

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
            if doctor_id in db.valid_doctor_ids:
                self.app.push_screen(DoctorMenu(doctor_id))
            else:
                self.notify("Invalid Doctor ID", severity="error")
        elif event.button.id == "back":
            self.app.pop_screen()


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
            valid_aadhar_numbers = db.get_valid_aadhar_numbers()
            if aadhar_number in valid_aadhar_numbers:
                self.app.push_screen(UserMenu(aadhar_number))
            else:
                self.notify("Invalid Aadhar Number", severity="error")
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
