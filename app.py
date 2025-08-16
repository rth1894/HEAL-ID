from textual.app import App
from screens.main_menu import MainMenu
from styles.app_styles import APP_CSS

class HEALID_App(App):
    CSS = APP_CSS

    def on_mount(self) -> None:
        self.push_screen(MainMenu())

