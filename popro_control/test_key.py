import dearpygui.dearpygui as dpg
from pynput import keyboard
import threading


# キー入力時の関数を定義
def on_press(key):
    #print (key)
    #print (dir(key))

    if 'value' in dir(key):
        #print (key.value,type(key.value),str(key.value))
        #print (dir(key.value))
        #print (key.value.char)
        if str(key.value) == '<174>':
            print ('----Start recording')

        elif str(key.value) == '<175>':
            print ('----Stop record')

    try:
        if key.char == 'a':  # 'a'キーの入力をキャプチャ
            print("Global A key was pressed!")
    except AttributeError:
        pass

# 別スレッドでグローバルキーイベントを監視
def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# スレッドを使ってキーボードリスナーを別で実行
key_listener_thread = threading.Thread(target=start_key_listener, daemon=True)
key_listener_thread.start()

# DearPyGuiのUI設定
dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="Example Window"):
    dpg.add_text("Press 'A' key (even when this window is not focused)")

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()