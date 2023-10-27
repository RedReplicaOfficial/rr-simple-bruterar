import os
import itertools
import rarfile
import zipfile
import threading
from time import gmtime, strftime, time, sleep
import PySimpleGUI as sg
import logging

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

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

def try_password(password, file_path):
    global total_tries, password_found, pause
    while pause:
        sleep(0.1)
    total_tries += 1
    try:
        if not os.path.exists(file_path):
            return "File does not exist."
        try:
            if file_path.lower().endswith(".rar"):
                with rarfile.RarFile(file_path) as archive:
                    archive.extractall(pwd=password)
                    password_found = True
                    return True
            elif file_path.lower().endswith(".zip"):
                with zipfile.ZipFile(file_path) as archive:
                    first_file = archive.namelist()[0]
                    with archive.open(first_file, 'r', pwd=bytes(password, "utf-8")) as file:
                        file.read()
                    password_found = True
                    return True
        except (rarfile.BadRarFile, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError):
            return f"{password},"
    except Exception as e:
        logging.error("Error in try_password function: " + str(e))

def calculate_stats():
    global start_time, total_tries, pause_time, pause, pause_start_time
    if pause:
        pause_time += time() - pause_start_time
        pause_start_time = time()
    elapsed_time = time() - start_time - pause_time
    average_tries_per_second = total_tries / elapsed_time if elapsed_time > 0 else 0
    average_tries_per_hour = average_tries_per_second * 3600
    elapsed_time_str = strftime("%H:%M:%S", gmtime(elapsed_time))
    display_text = f"{elapsed_time_str} | Tries: {total_tries} | Avg Tries/Min: {average_tries_per_second * 60:.2f} | Est. Avg Tries/Hour: {average_tries_per_hour:.2f}"
    return display_text

sg.theme('Dark Blue 3')  
layout = [[sg.Text('RRs Simple BruteRAR v1.0.3')],
          [sg.Input(key='-INPUT-', enable_events=True, size=(40, 1)), sg.FileBrowse(file_types=(("RAR files", "*.rar"), ("ZIP files", "*.zip")))],
          [sg.Button("Start"), sg.Button("Pause"), sg.Button("Resume"), sg.Button("Exit")],
          [sg.Text("", key='elapsed', size=(60, 1))],
          [sg.Output(size=(80, 20), key='-OUTPUT-')]]
window = sg.Window('RRs Simple BruteRAR v1.0.3', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break

    if event == 'Start':
        file_path = values['-INPUT-']
        if not file_path or not os.path.exists(file_path):
            sg.popup('Select a RAR or ZIP file first!')
        else:
            start_time = time()
            pause = False
            password_found = False
            total_tries = 0

            window['Start'].update(disabled=True)
            window['Pause'].update(disabled=False)
            threading.Thread(target=try_password, args=('password', file_path), daemon=True).start()

    elif event == 'Pause':
        pause = True
        pause_start_time = time()

    elif event == 'Resume':
        pause = False
        pause_time += time() - pause_start_time
        window['Resume'].update(disabled=True)

    elif event == '-THREAD-':  
        window.write_event_value('-UPDATE-', values[event])
        window['Start'].update(disabled=False)
        window['Pause'].update(disabled=True)

    elif event == '-UPDATE-':     
        window['-OUTPUT-'].update(values[event]+'\n', append=True)

window.close()
    except Exception as e:
        logging.error("Error in main : " + str(e))