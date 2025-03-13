import time
from threading import Thread
from tkinter import *
from tkinter import ttk
import pyautogui  # for controlling media player
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume


def get_audio_session(app_name):
    """Function to get the audio session for a specific app
    """
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name().lower() == app_name.lower():
            return session
    return None


def gradually_reduce_volume(session, duration, end_volume=0):
    """Function to gradually reduce volume for the media app
    """
    if session:
        audio_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        current_volume = audio_volume.GetMasterVolume()
        steps = 10
        step_time = duration / steps
        for step in range(steps):
            new_volume = current_volume - step * (current_volume - end_volume) / steps
            audio_volume.SetMasterVolume(new_volume, None)
            time.sleep(step_time)
        return current_volume  # Return the original volume so we can restore it later
    return None


def restore_volume(session, original_volume):
    """Function to restore the volume to its original value
    """
    if session:
        audio_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        audio_volume.SetMasterVolume(original_volume, None)
        print(f"Volume restored to {original_volume}")


def stop_media_playback(app_name):
    """Function to pause media playback
    """
    pyautogui.hotkey('playpause')  
    print(f"Playback paused for {app_name}")


def start_timer(duration_minutes, app_name, countdown):
    """Sleep timer function
    """
    session = get_audio_session(app_name)

    if not session:
        print(f"App {app_name} not found.")
        return
    
    print(f"Timer started for {duration_minutes} minutes...")
    duration_seconds = duration_minutes*60
    for remaining_seconds in range(duration_seconds,-1,-1):
        timer = secondsstotime(remaining_seconds)
        countdown.config(text=timer)
        time.sleep(1)


    #time.sleep(duration_minutes * 60)  # Wait for timer to complete

    print("Gradually reducing volume...")
    original_volume = gradually_reduce_volume(session, duration=60)  # Reduce volume over 60 seconds

    if original_volume is not None:
        print("Pausing playback...")
        stop_media_playback(app_name)
        
        # Restore the volume after pausing
        print("Restoring volume to original level...")
        restore_volume(session, original_volume)
    else:
        print("Failed to reduce volume or get initial volume level.")


def get_media_apps():
    """Function to get a list of currently running applications that are playing audio
    """
    media_apps = []
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name():
            media_apps.append(session.Process.name())
    return list(set(media_apps)) 


def start_countdown(countdown):
    """GUI using tkinter
    """
    try:
        timer_duration = int(entry.get())  # Get timer duration from user input
        app_name = app_var.get()  
        Thread(target=start_timer, args=(timer_duration, app_name, countdown)).start()   # New thread for start_timer() so the main gui isn't effected by time.sleep() function
    except ValueError:
        print("Invalid input. Please enter a valid number of minutes.")


def refresh_media_apps():
    """Function to refresh the dropdown list of media apps
    """
    media_apps = get_media_apps()
    app_var.set('')  # Clear the current selection
    dropdown['menu'].delete(0, 'end')  # Clear the dropdown menu
    for app in media_apps:
        dropdown['menu'].add_command(label=app, command=lambda value=app: app_var.set(value))
    app_var.set(media_apps[0] if media_apps else '')  # Set the default to the first app if available

def secondsstotime(seconds):
    """Function to convert seconds into hh:mm:ss format
    """
    hours = seconds//3600
    mins = (seconds%3600)//60
    seconds = (seconds%3600)%60
    if hours < 10:
        hours = f"0{hours}"
    else:
        hours = f"{hours}"
    if mins < 10:
        mins = f"0{mins}"
    else:
        mins = f"{mins}"
    if seconds < 10:
        seconds = f"0{seconds}"
    else:
        seconds = f"{seconds}"
    return f"{hours}:{mins}:{seconds}"

root = Tk()
root.title("Sleep Timer")

# Timer input field
Label(root, text="Set Timer (minutes):").grid(row=0, column=0, padx=10, pady=10)
entry = Entry(root)
entry.grid(row=0, column=1, padx=10, pady=10)

# Application dropdown list
Label(root, text="Select Media App:").grid(row=1, column=0, padx=10, pady=10)
app_var = StringVar(root)

# Create the dropdown menu with a default list
media_apps = get_media_apps()
app_var.set(media_apps[0] if media_apps else '')  # Set default app
dropdown = OptionMenu(root, app_var, *media_apps)
dropdown.grid(row=1, column=1, padx=10, pady=10)

# Refresh button to reload media apps
refresh_button = Button(root, text="Refresh Apps", command=refresh_media_apps)
refresh_button.grid(row=1, column=2, padx=10, pady=10)

# Countdown timer
countdown = Label(root, text="00:00:00")
countdown.grid(row=2, column=1, padx=10, pady=10)

# Start button
start_button = Button(root, text="Start Timer", command=lambda:start_countdown(countdown))
start_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)


# Run the GUI event loop
root.mainloop()
