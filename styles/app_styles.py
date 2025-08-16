
APP_CSS = """
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
