
import pytermgui as ptg
import pymysql

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

def main_menu():
    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "Heal - ID",
                "Sign in As",
                ptg.Button("User", lambda *_: user_signin()),
                ptg.Button("Doctor", lambda *_: doctor_signin(manager)),
                ptg.Button("Exit", lambda *_: manager.stop()),
            )
            .set_title("Main Menu")
            .center()
        )
        manager.add(window)

def user_signin():
    ptg.tim.print("[red]User sign-in not implemented yet.[/]")

def doctor_signin(manager):
    id_input = ptg.InputField(prompt="Enter your ID: ")
    id_input.prompt_style = ptg.tim.parse("[bold]")

    def submit_id(*_):
        value = id_input.value
        if value in valid_doctor_ids:
            show_doctor_form(manager, int(value))
        else:
            ptg.tim.print("[red]Invalid Doctor ID. Please try again.[/]")

    signin_window = (
        ptg.Window(
            "Doctor Sign-in",
            "",
            id_input,
            ptg.Button("Submit", submit_id),
            ptg.Button("Back", lambda *_: manager.remove(signin_window)),
        )
        .set_title("Doctor Sign-in")
        .center()
    )
    manager.add(signin_window)

def show_doctor_form(manager, doctor_id):
    cursor.execute("SELECT Doctor_Name, Specialization FROM Doctors WHERE Doctor_ID = %s", (doctor_id,))
    result = cursor.fetchone()
    if result:
        name, specialization = result
        form_window = (
            ptg.Window(
                f"Welcome, {name}",
                f"Specialization: {specialization}",
                "",
                ptg.Button("Start Consultation", lambda *_: start_consultation(doctor_id)),
                ptg.Button("Back", lambda *_: manager.remove(form_window)),
            )
            .set_title("Doctor Form")
            .center()
        )
        manager.add(form_window)
    else:
        ptg.tim.print("[red]Doctor not found.[/]")

def start_consultation(doctor_id):
    ptg.tim.print(f"[green]Starting consultation for Doctor ID: {doctor_id}[/]")

if __name__ == "__main__":
    main_menu()
