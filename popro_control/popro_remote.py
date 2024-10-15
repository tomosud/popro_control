
from pynput import keyboard
import threading

import popro_ui

def on_press_remo(key):
    if key == keyboard.Key.media_volume_up:
        print("Stop Recording!!")
        popro_ui.send_server_command_do(['stopRecording',0])
    elif key == keyboard.Key.media_volume_down:
        print("Recording!!")
        popro_ui.send_server_command_do(['startRecording',0])