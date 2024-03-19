import requests
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo


# command.py
def print_this():
    print("Command function is called.")
    
    r = requests.get('https://www.yahoo.co.jp/')
    print(r.content)


def save_callback():
    print("Save Clicked")

def ui():

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window"):
        dpg.add_text("Hello world")
        dpg.add_button(label="Save", callback=save_callback)
        dpg.add_input_text(label="string")
        dpg.add_slider_float(label="float")

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()




def demo():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()