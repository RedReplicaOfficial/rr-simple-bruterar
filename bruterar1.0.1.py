import rarfile 
import itertools 
import os 
import threading 
import time
from tkinter import filedialog, messagebox, Label, Button, Text, Tk, StringVar, END 

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_length = 14
log_interval = 100

root = Tk()
root.title("RR's Simple BruteRAR v1.0.0")

rar_file_path = StringVar()
log_text = Text(root)

rarfile.UNRAR_TOOL = r"C:\Program Files\WinRAR\UnRAR.exe"

start_time = 0
total_tries = 0
countdown_time = StringVar()

def browse_button():
    filename = filedialog.askopenfilename(filetypes=[('RAR files', '*.rar')])
    if filename == '':
        log_text.insert(END, "No file selected.\n")
        log_text.see(END)
        return
    elif not rarfile.is_rarfile(filename):
        log_text.insert(END, "This is not a .RAR file.\n")
        log_text.see(END)
        return
    elif not rarfile.RarFile(filename).needs_password():
        log_text.insert(END, "RAR file has no password to crack.\n")
        log_text.see(END)
        return
    rar_file_path.set(filename)

def try_password(password):
    global total_tries
    if not os.path.exists(rar_file_path.get()):
        log_text.insert(END, "RAR file does not exist.\n")
        log_text.see(END)
        return False
    try:
        with rarfile.RarFile(rar_file_path.get()) as archive:
            archive.extractall(pwd=password)
            return True
    except rarfile.BadRarFile:
        total_tries += 1
        log_text.insert(END, f"Attempted password: {password}\n")
        log_text.see(END)
        if int(log_text.index('end-1c').split('.')[0]) > 1000: 
            log_text.delete('1.0', '2.0')
        return False

def brute_force_password():
    global start_time, total_tries
    log_counter = 0
    start_time = time.time()
    for length in range(1, max_length + 1):
        password_combinations = itertools.product(charset, repeat=length)
        for password_tuple in password_combinations:
            password = ''.join(password_tuple)
            if try_password(password):
                elapsed_time = time.time() - start_time
                elapsed_time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
                speed = total_tries / (elapsed_time / 60)
                messagebox.showinfo("Password Cracked!", f"File has been cracked! Password is: {password}. It took {elapsed_time_str} Tries per minute: {speed:.2f}")
                return
            log_counter += 1
            if log_counter >= log_interval:
                log_text.insert(END, f"Logged {log_interval} password attempts.\n")
                log_counter = 0

def thread_it():
    t = threading.Thread(target=brute_force_password)
    t.start()

def update_label(dt):
    countdown_time.set(time.strftime("%H:%M:%S", time.gmtime(dt)))

def start_action():
    log_text.delete(1.0, END)
    log_text.insert(END, "Cracking in progress.\n")
    start_time = int(time.mktime(time.gmtime()))
    thread_it()
    update_timer(start_time)

def update_timer(start_time):
    dt = int(time.mktime(time.gmtime())) - start_time
    update_label(dt)
    root.after(1000, update_timer, start_time)  

info_text = "Made by Red Replica. Check out other useful softwares @ https://github.com/RedReplicaOfficial"
text_widget = Text(root, height=2, width=len(info_text))
text_widget.insert(1.0, info_text)
text_widget.configure(state='disabled', relief='flat')
text_widget.tag_configure("center", justify='center')
text_widget.tag_add("center", 1.0, "end")
text_widget.pack()
Button(text="Browse", command=browse_button).pack()
Button(text="Start", command=start_action).pack()

Label(root, textvariable=countdown_time).pack() 

Label(root, textvariable=rar_file_path, width=100).pack()
log_text.pack()

root.mainloop()