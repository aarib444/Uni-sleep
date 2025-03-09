import time
from threading import Thread
from tkinter import *
import pyautogui  # for controlling media player
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

# Function to get the audio session for a specific app
def get_audio_session(app_name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == app_name.lower():
            return session
    return None

# Function to gradually reduce volume for the media app:
def gradually_reduce_volume(session, duration, end_volume=0):
    if session:
        audio_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = audio_volume.GetMasterVolume()
        steps = 10
        step_time = duration / steps
        for step in range(steps):
            new_volume = current_volume - step * (current_volume - end_volume) / steps
            audio_volume.SetMasterVolume(new_volume, None)
            time.sleep(step_time)
        print(f"Volume reduced for {session.Process.name()}")

# Function to pause media playback
def stop_media_playback(app_name):
    if app_name.lower() == "vlc.exe":
        pyautogui.hotkey('space')  # VLC: spacebar to pause
    elif app_name.lower() in ["chrome.exe", "firefox.exe"]:
        pyautogui.hotkey('space')  # YouTube: spacebar to pause
    elif app_name.lower() == "spotify.exe":
        pyautogui.hotkey('playpause')  # Spotify: media key to pause
    print(f"Playback paused for {app_name}")

# Sleep timer function
def start_timer(duration_minutes, app_name):
    session = get_audio_session(app_name)

    if not session:
        print(f"App {app_name} not found.")
        return
    
    print(f"Timer started for {duration_minutes} minutes...")
    time.sleep(duration_minutes * 60)  # Wait for timer to complete

    print("Gradually reducing volume...")
    gradually_reduce_volume(session, duration=60)  # Reduce volume over 60 seconds

    print("Pausing playback...")
    stop_media_playback(app_name)

# GUI using tkinter
def start_countdown():
    try:
        timer_duration = int(entry.get())  # Get timer duration from user input
        app_name = app_entry.get().strip()  # Get app name (e.g., chrome.exe, vlc.exe)
        Thread(target=start_timer, args=(timer_duration, app_name)).start()
    except ValueError:
        print("Invalid input. Please enter a valid number of minutes.")

root = Tk()
root.title("Sleep Timer")

# Timer input field
Label(root, text="Set Timer (minutes):").grid(row=0, column=0, padx=10, pady=10)
entry = Entry(root)
entry.grid(row=0, column=1, padx=10, pady=10)

# Application input field
Label(root, text="App Name (e.g., chrome.exe, vlc.exe):").grid(row=1, column=0, padx=10, pady=10)
app_entry = Entry(root)
app_entry.grid(row=1, column=1, padx=10, pady=10)

# Start button
start_button = Button(root, text="Start Timer", command=start_countdown)
start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Run the GUI event loop
root.mainloop()
