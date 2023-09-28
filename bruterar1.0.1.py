# The usual/dependencies
import os
from time import time, strftime, gmtime
from threading import Thread
from tkinter import Tk, StringVar, Text, Button, Label, filedialog, END, messagebox
import itertools
import rarfile
import webbrowser

# Set the path to the UnRAR tool
rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

root = Tk()
root.title("RR's Simple BruteRAR v1.0.0")

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_length = 3
rar_file_path = StringVar(root)
log_text = Text(root)
label_text = StringVar(root)

start_time = 0
total_tries = 0
status_updater_interval = 0.5  # Updated to 0.5 seconds
clock_updater_interval = 0.5  # Updated to 0.5 seconds
password_found = False  # Track if the password is found

# Function to open the GitHub link
def open_github_link():
    webbrowser.open("https://github.com/RedReplicaOfficial")

# Function to stop the clock and counters
def stop_counters():
    global status_updater_interval, clock_updater_interval
    status_updater_interval = 0  # Stop status updater
    clock_updater_interval = 0  # Stop clock updater

# Add the text at the top and set it as a clickable label with warning text
header_text = "Made by Red Replica. Check out other useful software @ https://github.com/RedReplicaOfficial"
header_label = Label(root, text=header_text + "\n\nWarning: Your browser will open at the GitHub page if you click here!", cursor="hand2")
header_label.pack(padx=10, pady=10)
header_label.bind("<Button-1>", lambda e: open_github_link())

def browse_button():
    filename = filedialog.askopenfilename(filetypes=[('RAR files', '*.rar')])
    if filename == '':
        log_text.insert(END, "No file selected.\n")
        log_text.see(END)
        return
    elif not rarfile.is_rarfile(filename):
        log_text.insert(END, f"This is not a .rar file: {filename}\n")
        log_text.see(END)
        return
    elif not rarfile.RarFile(filename).needs_password():
        log_text.insert(END, "RAR file has no password to crack.\n")
        log_text.see(END)
        return
    rar_file_path.set(filename)

def safe_log_insert(text):
    if root.state() != "destroyed":
        log_text.insert(END, text)
        log_text.see(END)

def try_password(password):
    global total_tries, password_found
    if not os.path.exists(rar_file_path.get()):
        safe_log_insert("RAR file does not exist.\n")
        return False
    try:
        with rarfile.RarFile(rar_file_path.get()) as archive:
            archive.extractall(pwd=password)
            password_found = True
            stop_counters()  # Stop the counters when password is found
            return True
    except rarfile.BadRarFile:
        total_tries += 1
        safe_log_insert(f"Attempted password: {password}\n")
        if int(log_text.index('end-1c').split('.')[0]) > 1000:
            log_text.delete('1.0', '2.0')
        return False

def brute_force_password():
    global start_time, total_tries
    for length in range(1, max_length + 1):
        password_combinations = itertools.product(charset, repeat=length)
        for password_tuple in password_combinations:
            password = ''.join(password_tuple)
            if try_password(password):
                elapsed_time = time() - start_time
                elapsed_time_str = strftime("%d:%H:%M:%S", gmtime(elapsed_time))
                average_speed = total_tries / elapsed_time if elapsed_time > 0 else 0
                messagebox.showinfo("Password Cracked!", f"Password found! Password: {password}. Total time taken to crack: {elapsed_time_str}. Average tries/second: {average_speed:.2f}")
                return

def times_up():
    global start_time, total_tries
    if not password_found:
        elapsed_time = time() - start_time
        average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
        average_tries_per_hour = average_tries_per_second * 3600
        elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))

        # Create a formatted string to display next to the clock
        display_text = (
            f"{elapsed_time_str}     |     Tries: {total_tries}     |     "
            f"Avg Tries/Min: {average_tries_per_second * 60:.2f}     |     "
            f"Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
        )

        label_text.set(display_text)

        if root.state() != "destroyed":
            root.after(int(status_updater_interval * 1000), times_up)  # Updated interval

def start_brute_force():
    global start_time
    start_time = time()
    Thread(target=brute_force_password).start()
    times_up()

Button(root, text="Browse", command=browse_button).pack()
Button(root, text="Start", command=start_brute_force).pack()
Label(root, textvariable=label_text).pack()
Label(root, textvariable=rar_file_path, width=100).pack()
log_text.pack()

root.mainloop()
