import os
from time import time, strftime, gmtime
from threading import Thread
from tkinter import Tk, StringVar, Text, Button, Label, filedialog, END, messagebox
import itertools
import rarfile
import webbrowser

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"
root = Tk()
root.title("RR's Simple BruteRAR v1.0.3")

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_length = 14
rar_file_path = StringVar(root)
log_text = Text(root)
label_text = StringVar(root)
start_time = 0
total_tries = 0
status_updater_interval = 0.5
clock_updater_interval = 0.5
password_found = False
pause = False

def open_github_link():
    webbrowser.open("https://github.com/RedReplicaOfficial")

def stop_counters():
    global status_updater_interval, clock_updater_interval
    status_updater_interval = 0
    clock_updater_interval = 0

header_text = "Made by Red Replica"
header_label = Label(root, text=header_text, cursor="hand2")
header_label.pack(padx=10, pady=10)
header_label.bind("<Button-1>", lambda e: open_github_link())

def browse_button():
    filename = filedialog.askopenfilename(filetypes=[('RAR files', '*.rar')])
    if not filename:
        log_text.insert(END, "No file selected.")
        log_text.see(END)
    elif not rarfile.is_rarfile(filename):
        log_text.insert(END, f"This is not a .rar file")
        log_text.see(END)
    elif not rarfile.RarFile(filename).needs_password():
        log_text.insert(END, "RAR file has no password to crack.")
        log_text.see(END)
    else:
        rar_file_path.set(filename)
        pause_button.config(state="normal")

def safe_log_insert(text):
    if root.state() != "destroyed":
        log_text.insert(END, text)
        log_text.see(END)

def try_password(password):
    global total_tries, password_found, pause
    while pause:
        time.sleep(0.1)
    if not os.path.exists(rar_file_path.get()):
        safe_log_insert("RAR file does not exist.")
        return False
    try:
        with rarfile.RarFile(rar_file_path.get()) as archive:
            archive.extractall(path=r"C:\DestinationPath", pwd=password)
            password_found = True
            stop_counters()
            return True
    except rarfile.BadRarFile:
        total_tries += 1
        safe_log_insert(f"Attempted password: {password}")
        return False

def get_keyword_passwords():
    filename = filedialog.askopenfilename(filetypes=[('Text files', '*.txt')])
    if filename:
        with open(filename, 'r') as file:
            keywords = file.read()
        passwords = keywords.split(':')
        return passwords
    return None

def brute_force_password():
    global start_time, total_tries
    keyword_passwords = get_keyword_passwords()
    if keyword_passwords is not None:
        for password in keyword_passwords:
            if try_password(password):
                elapsed_time = time() - start_time
                elapsed_time_str = strftime("%d:%H:%M:%S", gmtime(elapsed_time))
                average_speed = total_tries / elapsed_time if elapsed_time > 0 else 0
                safe_log_insert(f"Password found! {password}")
                messagebox.showinfo("Password Cracked!", f"Password found! {password}")
                return
    for length in range(1, max_length + 1):
        password_combinations = itertools.product(charset, repeat=length)
        for password_tuple in password_combinations:
            password = ''.join(password_tuple)
            if try_password(password):
                elapsed_time = time() - start_time
                elapsed_time_str = strftime("%d:%H:%M:%S", gmtime(elapsed_time))
                average_speed = total_tries / elapsed_time if elapsed_time > 0 else 0
                safe_log_insert(f"Password found! {password}")
                messagebox.showinfo("Password Cracked!", f"Password found! {password}")
                return

def times_up():
    global start_time, total_tries
    if not password_found:
        elapsed_time = time() - start_time
        average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
        average_tries_per_hour = average_tries_per_second * 3600
        elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))
        display_text = (
            f"{elapsed_time_str} | Tries: {total_tries} | "
            f"Avg Tries/Min: {average_tries_per_second * 60:.2f} | "
            f"Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
        )

        label_text.set(display_text)

        if root.state() != "destroyed":
            root.after(int(status_updater_interval * 1000), times_up)

def start_brute_force():
    global start_time
    if rar_file_path.get() == '':
         messagebox.showinfo("No file selected", "Please select a file to crack.")
         return
    start_time = time()
    Thread(target=brute_force_password).start()
    times_up()
    start_button.config(state="disabled")
    pause_button.config(state="normal")
    resume_button.config(state="disabled")

def pause_brute_force():
    global pause
    pause = True
    resume_button.config(state="normal")

def resume_brute_force():
    global pause
    pause = False
    resume_button.config(state="disabled")

Button(root, text="Browse", command=browse_button).pack()
start_button = Button(root, text="Start", command=start_brute_force)
start_button.pack()

pause_button = Button(root, text="Pause", command=pause_brute_force, state="disabled")
pause_button.pack()

resume_button = Button(root, text="Resume", command=resume_brute_force, state="disabled")
resume_button.pack()
Label(root, textvariable=label_text).pack()
Label(root, textvariable=rar_file_path, width=100).pack()
log_text.pack()

root.mainloop()