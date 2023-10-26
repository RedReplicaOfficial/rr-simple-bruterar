import os
import itertools
import rarfile
import webbrowser
import threading
from time import gmtime, strftime, time, sleep
import PySimpleGUI as sg

rarfile.UNRAR_TOOL = os.path.join(os.environ['ProgramFiles'], "WinRAR", "UnRAR.exe")

charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
max_length = 14
start_time = 0
total_tries = 0
pause_start_time = 0
pause_time = 0
status_updater_interval = 0.5
clock_updater_interval = 0.5
password_found = False
pause = False


def stop_counters():
    global status_updater_interval, clock_updater_interval
    status_updater_interval = 0
    clock_updater_interval = 0


def browse_button():
    filename = sg.popup_get_file('Select RAR file.', file_types=(("RAR files", "*.rar"),))
    if not filename:
        return "No file selected."
    elif not rarfile.is_rarfile(filename):
        return f"This is not a .rar file"
    elif not rarfile.RarFile(filename).needs_password():
        return "RAR file has no password to crack."
    else:
        return f"Selected file: {filename}"


def try_password(password, rar_file_path):
    global total_tries, password_found, pause
    while pause:
        sleep(0.1)
    try:
        if not os.path.exists(rar_file_path):
            return "RAR file does not exist."
        try:
            with rarfile.RarFile(rar_file_path) as archive:
                archive.extractall(pwd=password)
                password_found = True
                stop_counters()
                return True
        except rarfile.BadRarFile:
            total_tries += 1
            return f"Failed with password: {password}, "
    except Exception as e:
        return "Error: " + str(e)


def display_password_found(password):
    elapsed_time = time() - start_time
    elapsed_time_str = strftime("%d:%H:%M:%S", gmtime(elapsed_time))
    average_speed = total_tries / elapsed_time if elapsed_time > 0 else 0
    return f"Password found! {password}"


def brute_force_password(window, rar_file_path):
    global start_time, total_tries
    for length in range(1, max_length + 1):
        password_combinations = itertools.product(charset, repeat=length)
        for password_tuple in password_combinations:
            password = ''.join(password_tuple)
            result = try_password(password, rar_file_path)
            if result == True:
                print(display_password_found(password))  # Use print() for debugging
                break
            else:
                print(result)  # Use print() for debugging


def times_up(window):
    global start_time, total_tries, pause, pause_time
    if pause:
        return
    if not password_found:
        elapsed_time = time() - start_time - pause_time
        average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
        average_tries_per_hour = average_tries_per_second * 3600
        elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))
        display_text = (
            f"{elapsed_time_str} | Tries: {total_tries} | "
            f"Avg Tries/Min: {average_tries_per_second * 60:.2f} | "
            f"Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
        )
        window['elapsed'].update(display_text)
        if window:
            window.refresh()
            window.after(int(status_updater_interval * 1000), times_up, window)


def start_brute_force(window, rar_file_path):
    global start_time, pause_time, pause
    pause_time = 0  # reset pause time on each start
    start_time = time()
    pause = False
    window['Start'].update(disabled=True)
    window['Pause'].update(disabled=False)
    threading.Thread(target=brute_force_password, args=(window, rar_file_path), daemon=True).start()
    times_up(window)


def pause_brute_force(window):
    global pause, pause_start_time
    pause = True
    pause_start_time = time() # Store pause start time
    window['Resume'].update(disabled=False)


def resume_brute_force(window):
    global pause, pause_time, pause_start_time
    pause = False
    pause_time += time() - pause_start_time  # Add pause time
    window['Resume'].update(disabled=True)
    times_up(window)


sg.theme('Dark Blue 3')  # Set theme

# GUI Layout
layout = [[sg.Text('RRs Simple BruteRAR v1.0.3')],
          [sg.Input(key='-INPUT-', enable_events=True, size=(40, 1)), sg.FileBrowse(file_types=(("RAR files", "*.rar"),))],
          [sg.Button("Start"), sg.Button("Pause"), sg.Button("Resume"), sg.Button("Exit")],
          [sg.Text("", key='elapsed', size=(60, 1))],
          [sg.Output(size=(80, 20), key='-OUTPUT-')]]

# Create the window
window = sg.Window('RRs Simple BruteRAR v1.0.3', layout)

# The event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == 'Start':
        rar_file_path = values['-INPUT-']
        if not rar_file_path or not os.path.exists(rar_file_path):
            sg.popup('Select a RAR file first!')
        else:
            start_brute_force(window, rar_file_path)
    elif event == 'Pause':
        pause_brute_force(window)
    elif event == 'Resume':
        resume_brute_force(window)
    elif event == '-THREAD-':         # Thread has completed
        window.write_event_value('-UPDATE-', values[event])
        window['Start'].update(disabled=False)
        window['Pause'].update(disabled=True)
    elif event == '-UPDATE-':        # Thread wants to communicate
        window['-OUTPUT-'].update(values[event]+'\n', append=True)


window.close()