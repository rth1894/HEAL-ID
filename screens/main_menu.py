from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Static
from .auth_screens import SignInOptions, RegisterOptions

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
