import tkinter as tk
from tkinter import messagebox, filedialog
import time
from datetime import datetime
import os
import shutil
import json
import stat
import psutil

# CONFIG
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"nextcloud_path": ""}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_var.set(folder_selected)

def save_and_exit():
    new_path = entry_var.get().strip()
    if not new_path:
        messagebox.showerror("Error", "Nextcloud path cannot be empty.")
        return
    config["nextcloud_path"] = new_path
    save_config(config)
    messagebox.showinfo("Saved", "Nextcloud path saved successfully.")
    root.destroy()

# Load config
config = load_config()

# --- UI ---
root = tk.Tk()
root.title("Nextcloud Path Settings")
root.geometry("550x180")
root.configure(bg="#f2f2f2")

# Fonts
label_font = ("Segoe UI", 11)
entry_font = ("Segoe UI", 10)
button_font = ("Segoe UI", 10, "bold")

# Frame
frame = tk.Frame(root, bg="#f2f2f2", padx=20, pady=20)
frame.pack(fill="both", expand=True)

# Label
label = tk.Label(frame, text="Select Nextcloud Destination Folder:", bg="#f2f2f2", font=label_font)
label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

# Entry
entry_var = tk.StringVar(value=config.get("nextcloud_path", ""))
entry = tk.Entry(frame, textvariable=entry_var, width=60, font=entry_font)
entry.grid(row=1, column=0, sticky="w", ipady=6)  # ipady increases the entry height

# Browse button (aligned horizontally with entry)
browse_button = tk.Button(frame, text="Browse", font=button_font, bg="#4285F4", fg="white", command=browse_folder)
browse_button.grid(row=1, column=1, padx=(10, 0), sticky="w", ipadx=10, ipady=6)

# Save button (just under browse button, aligned with it)
save_button = tk.Button(frame, text="Save", font=button_font, bg="#34A853", fg="white", command=save_and_exit)
save_button.grid(row=2, column=1, padx=(10, 0), pady=(10, 0), sticky="w", ipadx=18, ipady=6)

root.mainloop()

# Create GUI
class StatusWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Processing")
        self.root.geometry("400x120")  # Wider and taller
        self.root.attributes("-topmost", True)
        self.root.resizable(False, False)

        self.label = tk.Label(
            self.root,
            text="Starting...",
            font=("Arial", 14),  # Slightly larger font
            wraplength=380,      # Auto-wrap if too long
            justify="center"
        )
        self.label.pack(padx=20, pady=30)  # More padding

        self.root.lift()
        self.root.focus_force()

    def update_status(self, message):
        self.label.config(text=message)
        self.root.update_idletasks()

    def close(self):
        self.root.destroy()

# Supported file extensions (lowercase)
SUPPORTED_EXTENSIONS = [
        ".cr2",
        ".cr3",
        ".arw",
        ".dng",
        ".jpg",
        ".jpeg",
        ".heif",
        ".mp4",
        ".mov",
        ".mts",
        ".mxf",
        ".avi",
        ".xavc",
        ".wav",
        ".mp3",
        ".png"
    ]

# Function to get list of removable drives
def get_removable_drives():
    drives = []
    for part in psutil.disk_partitions():
        if 'removable' in part.opts or 'cdrom' in part.opts:
            drives.append(part.device)
    return drives

# Wait until a new drive is inserted
def wait_for_sd_card_async(status_win, on_detect):
    known_drives = set(get_removable_drives())

    def check_for_new_drive():
        nonlocal known_drives
        current_drives = set(get_removable_drives())
        new_drives = current_drives - known_drives
        if new_drives:
            drive = new_drives.pop()
            status_win.update_status(f"SD card detected at {drive}. Preparing files...")

            # Use drive as base path
            timestamp = int(time.time())
            tmp_folder = os.path.join(drive, f"device_{timestamp}")
            os.makedirs(tmp_folder, exist_ok=True)

            for item in os.listdir(drive):
                item_path = os.path.join(drive, item)
                if item_path == tmp_folder:
                    continue
                if os.path.isfile(item_path):
                    shutil.move(item_path, os.path.join(tmp_folder, item))
                elif os.path.isdir(item_path):
                    shutil.move(item_path, os.path.join(tmp_folder, item))

            status_win.close()
            on_detect(tmp_folder)
        else:
            status_win.root.after(2000, check_for_new_drive)

    status_win.update_status("Waiting for SD card...")
    check_for_new_drive()

# Wait until new file is created  Just  for testing!!!
# def wait_for_sd_card_async(base_path, status_win, on_detect):
#     existing = set(os.listdir(base_path))

#     def check_for_sd_card():
#         nonlocal existing
#         current = set(os.listdir(base_path))
#         new_items = current - existing
#         if new_items:
#             status_win.update_status("SD card detected. Preparing files...")
#             tmp_folder = os.path.join(base_path, f"device_{int(time.time())}")
#             os.makedirs(tmp_folder, exist_ok=True)

#             for item in new_items:
#                 item_path = os.path.join(base_path, item)
#                 if os.path.isfile(item_path):
#                     shutil.move(item_path, os.path.join(tmp_folder, item))
#                 elif os.path.isdir(item_path):
#                     shutil.move(item_path, os.path.join(tmp_folder, item))

#             status_win.close()
#             on_detect(tmp_folder)
#         else:
#             status_win.root.after(2000, check_for_sd_card)

#     status_win.update_status("Waiting for SD card...")
#     check_for_sd_card()

# User Input GUI
def show_metadata_form():
    metadata = {}

    def submit():
        metadata['client'] = client_entry.get()
        metadata['project'] = project_entry.get()
        metadata['date'] = date_entry.get()
        form.destroy()

    def cancel():
        form.destroy()

    form = tk.Tk()
    form.title("Enter Metadata")
    form.geometry("400x320")
    form.configure(bg="#f9f9f9")

    font_label = ("Arial", 12)
    font_entry = ("Arial", 14)  # Larger font makes entries taller

    tk.Label(form, text="Client Name:", bg="#f9f9f9", font=font_label).pack(pady=(12, 0))
    client_entry = tk.Entry(form, font=font_entry, width=25)
    client_entry.pack(ipady=6, pady=(0, 12))  # ipady increases inner padding (height)

    tk.Label(form, text="Project Title:", bg="#f9f9f9", font=font_label).pack(pady=(5, 0))
    project_entry = tk.Entry(form, font=font_entry, width=25)
    project_entry.pack(ipady=6, pady=(0, 12))

    tk.Label(form, text="Shoot Date (YYYY-MM-DD):", bg="#f9f9f9", font=font_label).pack(pady=(5, 0))
    date_entry = tk.Entry(form, font=font_entry, width=25)
    date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))
    date_entry.pack(ipady=6, pady=(0, 18))

    btn_frame = tk.Frame(form, bg="#f9f9f9")
    btn_frame.pack(pady=5)
    tk.Button(btn_frame, text="Submit", command=submit, width=12, font=font_label).pack(side="left", padx=20)
    tk.Button(btn_frame, text="Cancel", command=cancel, width=12, font=font_label).pack(side="right", padx=20)

    form.mainloop()
    return metadata if metadata else None

# Copy files from SD card to Nextcloud folder with renaming, then delete originals
def copy_and_rename_files(sd_path, nextcloud_path, metadata, status_win=None):
    client = metadata['client'].replace(' ', '_')
    project = metadata['project'].replace(' ', '_')
    shoot_date = metadata['date']

    dest_folder_name = f"{client}_{shoot_date}"
    dest_folder = os.path.join(nextcloud_path, dest_folder_name)
    os.makedirs(dest_folder, exist_ok=True)

    file_counter = {}
    total_files = 0

    # Step 1: Count all matching files, including in the root
    for root, dirs, files in os.walk(sd_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in SUPPORTED_EXTENSIONS:
                total_files += 1

    processed = 0

    # Step 2: Copy and rename files
    for root, dirs, files in os.walk(sd_path):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue  # Skip unsupported files

            base_filename = f"{shoot_date}_{client}_{project}"

            if base_filename not in file_counter:
                file_counter[base_filename] = 1

            new_filename = f"{base_filename}_{file_counter[base_filename]:02d}{ext}"
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_folder, new_filename)

            while os.path.exists(dest_file):
                file_counter[base_filename] += 1
                new_filename = f"{base_filename}_{file_counter[base_filename]:02d}{ext}"
                dest_file = os.path.join(dest_folder, new_filename)

            try:
                if status_win:
                    status_win.update_status(f"Copying {file} ({processed + 1} of {total_files})...")

                shutil.copy2(src_file, dest_file)
                print(f"Copied {src_file} -> {dest_file}")

                try:
                    os.chmod(src_file, stat.S_IWRITE)  # Make sure file is deletable
                    os.remove(src_file)
                    print(f"Deleted original {src_file}")
                except Exception as e:
                    print(f"⚠️ Could not delete {src_file}: {e}")

                file_counter[base_filename] += 1
                processed += 1

            except Exception as e:
                print(f"❌ Failed to copy {src_file}: {e}")
                continue

    # Delete empty source folders after files processed
    try:
        # Walk the source path bottom-up to delete empty folders
        for root, dirs, files in os.walk(sd_path, topdown=False):
            if not os.listdir(root):  # if folder empty
                os.rmdir(root)
                print(f"Deleted empty folder {root}")
    except Exception as e:
        print(f"Could not delete empty folders in source path: {e}")

    if status_win:
        status_win.update_status("Copy and delete completed.")
        status_win.root.after(1500, status_win.close)
        status_win.root.mainloop()
    else:
        print("✅ Copy and delete completed.")

# ---- Main Workflow ----
def on_sd_card_detected(sd_card_path):
    metadata = show_metadata_form()
    if metadata:
        nextcloud_path = config["nextcloud_path"]
        status_win = StatusWindow()
        copy_and_rename_files(sd_card_path, nextcloud_path, metadata, status_win)

        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        cont = messagebox.askyesno("Continue?", "Media ingest completed.\nDo you want to ingest another SD card?", parent=root)
        root.attributes('-topmost', False)
        root.destroy()
        if cont:
            start_sd_wait_loop()
    else:
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Cancelled", "Operation cancelled by user.")
        root.destroy()

def start_sd_wait_loop():
    status_win = StatusWindow()
    # wait_for_sd_card_async("D:/TestMounts", status_win, on_sd_card_detected)
    wait_for_sd_card_async(status_win, on_sd_card_detected)

if __name__ == "__main__":
    start_sd_wait_loop()
    tk.mainloop()