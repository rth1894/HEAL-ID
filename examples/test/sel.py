import pytermgui as ptg
import pymysql

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
print(valid_doctor_ids)

def main_menu():
    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "Medical System",
                "Sign in As",
                ptg.Button("User", lambda *_: user_signin()),
                ptg.Button("Doctor", lambda *_: doctor_signin()),
                ptg.Button("Exit", lambda *_: manager.stop()),
            )
            .set_title("Main Menu")
            .center()
        )
        manager.add(window)

def user_signin():
    # Placeholder for user sign-in functionality
    ptg.tim.print("[red]User sign-in not implemented yet.[/]")

def doctor_signin():
    with ptg.WindowManager() as manager:
        id_input = ptg.InputField(prompt="Enter your ID: ")
        id_input.prompt_style = ptg.tim.parse("[bold]")  # Make prompt bold and non-editable

        def submit_id(*_):
            value = id_input.value
            if value in valid_doctor_ids:
                show_doctor_form(int(value))
            else:
                ptg.tim.print("[red]Invalid Doctor ID. Please try again.[/]")

        window = (
            ptg.Window(
                "Doctor Sign-in",
                "",
                id_input,
                ptg.Button("Submit", submit_id),
                ptg.Button("Back", lambda *_: manager.stop()),
            )
            .set_title("Doctor Sign-in")
            .center()
        )

        # Override the default key_press method to prevent editing the prompt
        def custom_key_press(self, key):
            if key == "backspace" and self.cursor_position <= len(self.prompt):
                return
            if self.cursor_position <= len(self.prompt):
                self.cursor_position = len(self.prompt)
            super(ptg.InputField, self).key_press(key)

        id_input.key_press = custom_key_press.__get__(id_input, ptg.InputField)

        manager.add(window)

def show_doctor_form(doctor_id):
    # Fetch doctor details from the database
    cursor.execute("SELECT name, age, gender FROM Doctors WHERE Doctor_ID = %s", (doctor_id,))
    result = cursor.fetchone()

    if result:
        name, age, gender = result
        with ptg.WindowManager() as manager:
            window = (
                ptg.Window(
                    f"Welcome, Dr. {name}",
                    f"Age: {age}",
                    f"Gender: {gender}",
                    "",
                    ptg.Button("Start Consultation", lambda *_: start_consultation(doctor_id)),
                    ptg.Button("Back", lambda *_: manager.stop()),
                )
                .set_title("Doctor Form")
                .center()
            )
            manager.add(window)
    else:
        ptg.tim.print("[red]Doctor not found.[/]")

def start_consultation(doctor_id):
    # Placeholder for starting a consultation
    ptg.tim.print(f"[green]Starting consultation for Doctor ID: {doctor_id}[/]")

if __name__ == "__main__":
    main_menu()
