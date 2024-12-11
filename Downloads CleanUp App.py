import os
import shutil
import datetime
import json
from send2trash import send2trash
import FreeSimpleGUI as sg

# Configuration file path (use absolute path to avoid issues with __file__ in IDLE)
config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup_config.json")

# Load configuration
def load_config():
    print(f"Checking for configuration file at: {config_file}")
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            return json.load(file)
    return {}

# Save configuration
def save_config(config):
    with open(config_file, "w") as file:
        json.dump(config, file, indent=4)

# GUI Setup for Configuration
def setup_config_gui():
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("Welcome to the Downloads Cleanup Setup!")],
        [sg.Text("Please specify the following settings:")],
        [sg.Text("Downloads Folder", size=(20, 1)), sg.Input(key='-DOWNLOADS-'), sg.FolderBrowse()],
        [sg.Text("To Be Deleted Folder", size=(20, 1)), sg.Input(key='-TO_BE_DELETED-'), sg.FolderBrowse()],
        [sg.Text("Exempt Folder", size=(20, 1)), sg.Input(key='-EXEMPT-'), sg.FolderBrowse()],
        [sg.Text("Cleanup Interval (days)", size=(20, 1)), sg.Input(default_text="7", key='-INTERVAL-')],
        [sg.Button('Submit'), sg.Button('Cancel')]
    ]

    window = sg.Window("Setup", layout)

    while True:
        event, values = window.read()

        # Handle Cancel or Window Close
        if event in (sg.WINDOW_CLOSED, 'Cancel'):
            sg.popup("Setup canceled.", title="Canceled")
            window.close()
            return None

        # Handle Submit
        if event == 'Submit':
            try:
                # Collect and validate user inputs
                downloads_folder = values['-DOWNLOADS-']
                to_be_deleted_folder = values['-TO_BE_DELETED-']
                exempt_folder = values['-EXEMPT-']
                cleanup_interval = int(values['-INTERVAL-'])  # Ensure it's an integer

                if not downloads_folder or not to_be_deleted_folder or not exempt_folder:
                    raise ValueError("All folder paths must be specified.")

                # Build the configuration dictionary
                config = {
                    "downloads_folder": downloads_folder,
                    "to_be_deleted_folder": to_be_deleted_folder,
                    "exempt_folder": exempt_folder,
                    "cleanup_interval_days": cleanup_interval,
                    "last_cleanup": ""
                }

                # Save and notify the user
                save_config(config)
                sg.popup("Setup complete! Configuration saved.", title="Success")
                window.close()
                return config

            except ValueError as e:
                sg.popup(f"Error: {str(e)}", title="Validation Error")

# Function to show pop-ups
def show_popup(title, message):
    sg.popup(message, title=title)

# Function to move old files
def move_old_files(config):
    downloads_folder = config["downloads_folder"]
    to_be_deleted_folder = config["to_be_deleted_folder"]
    exempt_folder = config["exempt_folder"]

    # Get today's date as a string (e.g., "2024-12-11")
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_folder = os.path.join(to_be_deleted_folder, today_date)

    # Ensure the daily subfolder exists
    os.makedirs(daily_folder, exist_ok=True)

    print(f"Checking files in {downloads_folder}")
    now = datetime.datetime.now()
    moved_files = 0

    for file_name in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, file_name)

        # Skip the "To Be Deleted" folder and exempt folder
        if file_path in [to_be_deleted_folder, exempt_folder]:
            continue

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # Get the file's last modified time
            file_age = now - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age > datetime.timedelta(hours=24):
                # Move the file into the dated subfolder
                shutil.move(file_path, daily_folder)
                moved_files += 1

    # Show a pop-up notification
    show_popup("Daily Cleanup Complete", f"{moved_files} file(s) moved to '{daily_folder}'.")

# Function to clean up "To Be Deleted" folder
def clean_up(config):
    to_be_deleted_folder = config["to_be_deleted_folder"]
    deleted_files = 0
    missing_files = 0  # Track how many files were missing

    print(f"Cleaning up files in {to_be_deleted_folder}")
    for file_name in os.listdir(to_be_deleted_folder):
        file_path = os.path.join(to_be_deleted_folder, file_name)

        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            try:
                send2trash(file_path)
                deleted_files += 1
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")
        else:
            print(f"File not found (skipping): {file_path}")
            missing_files += 1

    # Show a pop-up notification
    show_popup(
        "Weekly Cleanup Complete",
        f"{deleted_files} file(s) sent to the Recycle Bin.\n{missing_files} file(s) were missing and skipped.",
    )

# Main script logic
def main():
    config = load_config()

    if not config:
        print("Configuration file not found or invalid. Launching setup.")
        config = setup_config_gui()
        if not config:
            print("Setup was canceled. Exiting.")
            return
    else:
        print("Configuration loaded successfully.")

    # Perform daily tasks
    move_old_files(config)

    # Schedule cleanup based on interval
    cleanup_interval_days = config.get("cleanup_interval_days", 7)
    last_cleanup = config.get("last_cleanup", "")

    if not last_cleanup or (datetime.datetime.now() - datetime.datetime.fromisoformat(last_cleanup)).days >= cleanup_interval_days:
        clean_up(config)
        config["last_cleanup"] = datetime.datetime.now().isoformat()
        save_config(config)

# Run the program
if __name__ == "__main__":
    main()
