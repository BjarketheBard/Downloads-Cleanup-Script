import os
import shutil
import datetime
from send2trash import send2trash
import ctypes
import pymsgbox  # Ensure consistent imports at the top

# Paths
downloads_folder = r"C:\Users\Bryan\Downloads"
to_be_deleted_folder = os.path.join(downloads_folder, "To Be Deleted")
exempt_folder = os.path.join(downloads_folder, "Files to Back Up")

# Ensure the "To Be Deleted" folder exists
os.makedirs(to_be_deleted_folder, exist_ok=True)

# Pop-up function
def show_popup(title, message):
    # Using pymsgbox for consistent and customizable pop-ups
    pymsgbox.alert(message, title)

# Function to move old files
def move_old_files():
    now = datetime.datetime.now()
    moved_files = 0

    for file_name in os.listdir(downloads_folder):
        file_path = os.path.join(downloads_folder, file_name)
        
        # Skip the "To Be Deleted" folder and the exempt folder
        if file_path in [to_be_deleted_folder, exempt_folder]:
            continue

        # Check if it's a file and not a directory
        if os.path.isfile(file_path):
            # Get the file's last modified time
            file_age = now - datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_age > datetime.timedelta(hours=24):
                shutil.move(file_path, to_be_deleted_folder)
                moved_files += 1

    # Show a pop-up notification
    show_popup("Daily Cleanup Complete", f"{moved_files} file(s) moved to 'To Be Deleted'.")

# Function to clean up "To Be Deleted" folder
def clean_up():
    deleted_files = 0

    for file_name in os.listdir(to_be_deleted_folder):
        file_path = os.path.join(to_be_deleted_folder, file_name)
        send2trash(file_path)
        deleted_files += 1

    # Show a pop-up notification
    show_popup("Weekly Cleanup Complete", f"{deleted_files} file(s) sent to the Recycle Bin.")

# Run daily tasks
move_old_files()

# Schedule cleanup on Sunday afternoon
if datetime.datetime.now().weekday() == 6 and datetime.datetime.now().hour >= 12:
    clean_up()
