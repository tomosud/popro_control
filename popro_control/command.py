import requests
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json


setting_dict = {'key1': 'value1', 'key2': 'value2'}


def save_settings(setting_dict, file_name='tool_setting.ini'):
    with open(file_name, 'w') as file:
        json.dump(setting_dict, file)

def load_settings(file_name='tool_setting.ini'):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_name}' not found. Returning empty dictionary.")
        return {}

def check_url(url):
    try:
        response = requests.get(url)
        # 200〜299のステータスコードは成功を示す
        if response.status_code >= 200 and response.status_code < 300:
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.exceptions.RequestException as e:
        # リクエストに関するエラーの処理
        return False, str(e)


# command.py
def print_this():
    print("Command function is called.")
    
    r = requests.get('https://www.yahoo.co.jp/')
    print(r.content)


def save_callback():
    print("Save Clicked")
    print_this()

    # 使用例
    # 保存

    save_settings(setting_dict)

    # 読み込み
    loaded_settings = load_settings()
    print(loaded_settings)  # {'key1': 'value1', 'key2': 'value2'}    

def add_ui_test():
    dpg.add_text("Hello worldBB")
    dpg.add_button(label="Save", callback=save_callback)

def ui():

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window"):
        dpg.add_text("Hello world")
        dpg.add_button(label="Save", callback=save_callback)
        dpg.add_input_text(label="string")
        dpg.add_slider_float(label="float")
        add_ui_test()

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


def demoui():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

def get(work=0):

    url = "http://172.22.148.51:8080/gp/gpMediaList"

    if work == 1:
        url = "http://172.22.548.51:8080/gp/gpMediaList"

    e = check_url(url)

    print (e)
    

