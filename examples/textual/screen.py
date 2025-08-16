from textual.app import App, ComposeResult
from textual.widgets import Button, Label, Static
from textual.containers import Container

class MainScreen(Static):
    def compose(self) -> ComposeResult:
        yield Container(
            Label("Health Database App", id="title"),
            Button("Doctor Sign In", id="doctor_signin"),
            Button("Exit", id="exit"),
            id="main_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit":
            self.app.exit()
        elif event.button.id == "doctor_signin":
            self.notify("Doctor Sign In pressed")

class HealthDatabaseApp(App):
    CSS = """
    #main_container {
        width: 100%;
        height: 100%;
        align: center middle;
    }

    #title {
        text-align: center;
        width: 100%;
        height: 3;
        color: $text;
    }

    Button {
        width: 50%;
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield MainScreen()

if __name__ == "__main__":
    app = HealthDatabaseApp()
    app.run()
