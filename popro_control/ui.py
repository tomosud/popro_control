

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

import command as cm
import uuid

gopro_dict = {}

temp_popro_ui_dict = {}


def ret_uitag(name_str,memo):

    global temp_popro_ui_dict

    uuidnow = str(uuid.uuid4())

    temp_popro_ui_dict[uuidnow] = {'name':name_str,'memo':memo}

    return uuidnow

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

    dpg.add_button(label="Record!!", callback=save_callback,width=300, height=100)

def beep():
    print('beep')

def send_map(sender, app_data, user_data):

    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    cm.command_send(user_data,'beep_mute')
    cm.command_send(user_data,'beep')

    m = cm.ret_all_media(url=user_data)

    print ('media',m)

def add_button_gopros(parent):

    global temp_popro_ui_dict
    global gopro_dict

    temp_popro_ui_dict['gopro_single_buttons'] = []

    #print ('add_button_gopros')

    for o in gopro_dict.keys():

        print ('gopro_single_buttons',o)

        tag = ret_uitag(o,gopro_dict[o]['name'])
        temp_popro_ui_dict['gopro_single_buttons'].append(tag)

        print ('tag---',tag)

        label = gopro_dict[o]['name'].replace(' ','\n')

        dpg.add_button(label=label,parent=parent,tag=temp_popro_ui_dict['gopro_single_buttons'][-1],callback=send_map,user_data=o,width=75, height=100)


def add_button_command(parant,command):

    pass


def main():
    global gopro_dict
    gopro_dict = cm.ret_gopros()

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window"):
        dpg.add_text("Hello world")
        #dpg.add_button(label="Save", callback=save_callback)
        #dpg.add_input_text(label="string")
        #dpg.add_slider_float(label="float")
        add_ui_test()

        with dpg.menu_bar():
            dpg.add_menu(label="Menu Options")

        with dpg.child_window(autosize_x=True, height=95):
            with dpg.group(horizontal=True):

                parent=dpg.last_item()
                add_button_gopros(parent)

                '''
                dpg.add_button(label='test', parent=dpg.last_item(),tag='test_button',callback=send_map,user_data='temp444')

                dpg.add_button(label="Header 1", width=75, height=75)
                dpg.add_button(label="Header 2", width=75, height=75)
                dpg.add_button(label="Header 3", width=75, height=75)
                dpg.add_button(label="Header 1", width=75, height=75)
                dpg.add_button(label="Header 2", width=75, height=75)    
                
                '''


        with dpg.child_window(autosize_x=True, height=175):
            with dpg.group(horizontal=True, width=0):

                with dpg.child_window(width=100, height=150):
                    dpg.add_button(label="Button 1")
                    dpg.add_button(label="Button 2")
                    dpg.add_button(label="Button 3")
                with dpg.child_window(width=100, height=150):
                    dpg.add_button(label="Button 1")
                    dpg.add_button(label="Button 2")
                    dpg.add_button(label="Button 3")
                with dpg.child_window(width=100, height=150):
                    dpg.add_button(label="Button 1")
                    dpg.add_button(label="Button 2")
                    dpg.add_button(label="Button 3")

        with dpg.group(horizontal=True):
            dpg.add_button(label="Footer 1", width=175)
            dpg.add_text("Footer 2")
            dpg.add_button(label="Footer 3", width=175)

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

