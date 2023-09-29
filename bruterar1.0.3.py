# Import necessary modules
import os  # This module provides functions for interacting with the operating system.
from time import time, strftime, gmtime  # These are used for time-related operations.
from threading import Thread  # Threading is used for parallel processing.
from tkinter import Tk, StringVar, Text, Button, Label, filedialog, END, messagebox  # For creating a GUI.
import itertools  # Used for generating combinations.
import rarfile  # A library for working with RAR files.
import webbrowser  # To open a web link.

# Configure the path to the UnRAR tool (assuming you have WinRAR installed)
rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

# Create the main application window
root = Tk()
root.title("RR's Simple BruteRAR v1.0.3")

# Define character set and maximum password length
charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_length = 14

# Create a StringVar to hold the RAR file path
rar_file_path = StringVar(root)

# Create a Text widget for logging
log_text = Text(root)

# Create a StringVar to hold label text
label_text = StringVar(root)

# Initialize global variables
start_time = 0
total_tries = 0
status_updater_interval = 0.5  # Update interval for status
clock_updater_interval = 0.5  # Update interval for clock
password_found = False

# Function to open the GitHub link
def open_github_link():
    webbrowser.open("https://github.com/RedReplicaOfficial")

# Function to stop updating counters
def stop_counters():
    global status_updater_interval, clock_updater_interval
    status_updater_interval = 0
    clock_updater_interval = 0

# Application header text
header_text = "Made by Red Replica. Check out other useful software @ https://github.com/RedReplicaOfficial"

# Create a label with a clickable link to GitHub
header_label = Label(root, text=header_text + "\n\nWarning: Your browser will open at the GitHub page if you click here!", cursor="hand2")
header_label.pack(padx=10, pady=10)
header_label.bind("<Button-1>", lambda e: open_github_link())

# Function to browse for a RAR file
def browse_button():
    filename = filedialog.askopenfilename(filetypes=[('RAR files', '*.rar')])
    if not filename:
        log_text.insert(END, "No file selected.\n")
        log_text.see(END)
    elif not rarfile.is_rarfile(filename):
        log_text.insert(END, f"This is not a .rar file: {filename}\n")
        log_text.see(END)
    elif not rarfile.RarFile(filename).needs_password():
        log_text.insert(END, "RAR file has no password to crack.\n")
        log_text.see(END)
    rar_file_path.set(filename)

# Function to safely insert text into the log Text widget
def safe_log_insert(text):
    if root.state() != "destroyed":
        log_text.insert(END, text)
        log_text.see(END)

# Function to try a password
def try_password(password):
    global total_tries, password_found
    if not os.path.exists(rar_file_path.get()):
        safe_log_insert("RAR file does not exist.\n")
        return False
    try:
        with rarfile.RarFile(rar_file_path.get()) as archive:
            archive.extractall(path=r"C:\DestinationPath", pwd=password)  # Specify a path here
            password_found = True
            stop_counters()
            return True
    except rarfile.BadRarFile:
        total_tries += 1
        safe_log_insert(f"Attempted password: {password}\n")
        if int(log_text.index('end-1c').split('.')[0]) > 1000:
            log_text.delete('1.0', '2.0')
        return False

# Function to perform brute force password cracking
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
                safe_log_insert(f"\n\nPassword found! Password: {password}.\nTotal time taken to crack: {elapsed_time_str}.\nAverage tries/second: {average_speed:.2f}\n")
                messagebox.showinfo("Password Cracked!", f"Password found! Password: {password}. Total time taken to crack: {elapsed_time_str}. Average tries/second: {average_speed:.2f}")
                start_button.config(state="normal")
                return

# Function to update the timer and statistics
def times_up():
    global start_time, total_tries
    if not password_found:
        elapsed_time = time() - start_time
        average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
        average_tries_per_hour = average_tries_per_second * 3600
        elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))

        display_text = (
            f"{elapsed_time_str}     |     Tries: {total_tries}     |     "
            f"Avg Tries/Min: {average_tries_per_second * 60:.2f}     |     "
            f"Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
        )

        label_text.set(display_text)

        if root.state() != "destroyed":
            root.after(int(status_updater_interval * 1000), times_up)

# Function to start brute force password cracking
def start_brute_force():
    global start_time
    start_time = time()
    Thread(target=brute_force_password).start()
    times_up()
    start_button.config(state="disabled")

# Create a Browse button
Button(root, text="Browse", command=browse_button).pack()

# Create a Start button
start_button = Button(root, text="Start", command=start_brute_force)
start_button.pack()

# Create a label to display statistics
Label(root, textvariable=label_text).pack()

# Create a label to display the selected RAR file path
Label(root, textvariable=rar_file_path, width=100).pack()

# Create the log Text widget
log_text.pack()

# Start the main event loop
root.mainloop()
