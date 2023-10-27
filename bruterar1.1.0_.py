import os
import itertools
import rarfile
import threading
from time import gmtime, strftime, time, sleep
import PySimpleGUI as sg
import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

try:
    rarfile.UNRAR_TOOL = os.path.join(os.environ['ProgramFiles'], "WinRAR", "UnRAR.exe")
except Exception as e:
    logging.error("Error setting up UNRAR_TOOL: " + str(e))
    raise e

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
    try:
        filename = sg.popup_get_file('Select RAR file.', file_types=(("RAR files", "*.rar"),))
        if not filename:
            return "No file selected."
        elif not rarfile.is_rarfile(filename):
            return f"This is not a .rar file"
        elif not rarfile.RarFile(filename).needs_password():
            return "RAR file has no password to crack."
        else:
            return f"Selected file: {filename}"
    except Exception as e:
        logging.error("Error in browse_button function: " + str(e))


def try_password(password, rar_file_path):
    global total_tries, password_found, pause
    while pause:
        sleep(0.1)
    total_tries += 1
    try:
        if not os.path.exists(rar_file_path):
            return "RAR file does not exist."
        try:
            with rarfile.RarFile(rar_file_path) as archive:
                archive.extractall(pwd=password)
                password_found = True
                return True
        except rarfile.BadRarFile:
            return f"{password}, "
    except Exception as e:
        logging.error("Error in try_password function: " + str(e))


def display_password_found(password):
    try:
        elapsed_time = time() - start_time
        elapsed_time_str = strftime("%d:%H:%M:%S", gmtime(elapsed_time))
        average_speed = total_tries / elapsed_time if elapsed_time > 0 else 0
        return f"Password found! {password}"
    except Exception as e:
        logging.error("Error in display_password_found function: " + str(e))
 

def brute_force_password(window, rar_file_path):
    global start_time, total_tries
    try:
        for length in range(1, max_length + 1):
            password_combinations = itertools.product(charset, repeat=length)
            for password_tuple in password_combinations:
                password = ''.join(password_tuple)
                result = try_password(password, rar_file_path)
                if result == True:
                    print(display_password_found(password))
                    window.write_event_value('-THREAD-', '')
                    return
                else:
                    print(result)
    except Exception as e:
        logging.error("Error in brute_force_password function: " + str(e))


def calculate_stats():
    global start_time, total_tries, pause_time, pause, pause_start_time
    if pause:
        pause_time += time() - pause_start_time
        pause_start_time = time()
    elapsed_time = time() - start_time - pause_time
    average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
    average_tries_per_hour = average_tries_per_second * 3600
    elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))
    display_text = (
        f"{elapsed_time_str} | Tries: {total_tries} | "
        f"Avg Tries/Min: {average_tries_per_second * 60:.2f} | "
        f"Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
    )
    return display_text


def update_display(window):
    global password_found
    while not password_found:
        sleep(status_updater_interval)
        window['elapsed'].update(calculate_stats())
        window.refresh()


def start_brute_force(window, rar_file_path):
    global start_time, pause_time, pause
    try:
        pause_time = 0  
        start_time = time()
        pause = False
        window['Start'].update(disabled=True)
        window['Pause'].update(disabled=False)
        threading.Thread(target=brute_force_password, args=(window, rar_file_path), daemon=True).start()
        threading.Thread(target=update_display, args=(window,), daemon=True).start()
    except Exception as e:
        logging.error("Error in start_brute_force function: " + str(e))


def pause_brute_force(window):
    global pause, pause_start_time
    try:
        pause = True
        pause_start_time = time()  # Store pause start time
        window['Resume'].update(disabled=False)
    except Exception as e:
        logging.error("Error in pause_brute_force function: " + str(e))


def resume_brute_force(window):
    global pause, pause_time, pause_start_time
    try:
        pause = False
        pause_time += time() - pause_start_time  
        window['Resume'].update(disabled=True)
    except Exception as e:
        logging.error("Error in resume_brute_force function: " + str(e))

try:
    sg.theme('Dark Blue 3')  
    layout = [[sg.Text('RRs Simple BruteRAR v1.0.3')],
              [sg.Input(key='-INPUT-', enable_events=True, size=(40, 1)), sg.FileBrowse(file_types=(("RAR files", "*.rar"),))],
              [sg.Button("Start"), sg.Button("Pause"), sg.Button("Resume"), sg.Button("Exit")],
              [sg.Text("", key='elapsed', size=(60, 1))],
              [sg.Output(size=(80, 20), key='-OUTPUT-')]]
    window = sg.Window('RRs Simple BruteRAR v1.0.3', layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        elif event == 'Start':
            rar_file_path = values['-INPUT-']
            if not rar_file_path or not os.path.exists(rar_file_path):
                sg.popup('Select a RAR file first!')
            else:
                try:
                    start_brute_force(window, rar_file_path)
                except Exception as e:
                    logging.error('Error while starting the brute force: ' + str(e))
                    raise e  
        elif event == 'Pause':
            pause_brute_force(window)
        elif event == 'Resume':
            resume_brute_force(window)
        elif event == '-THREAD-':        
            window.write_event_value('-UPDATE-', values[event])
            window['Start'].update(disabled=False)
            window['Pause'].update(disabled=True)
        elif event == '-UPDATE-':        
            window['-OUTPUT-'].update(values[event]+'\n', append=True)
    window.close()
except Exception as e:
    logging.error("Error in main : " + str(e))