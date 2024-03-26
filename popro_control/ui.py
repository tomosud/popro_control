

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

import command as cm
import uuid

gopro_dict = {}
temp_popro_ui_dict = {}

temp_files_dict = {}

gopro_recording = False

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


def recording():
    
    global gopro_recording

    #あとで並列処理に変更する（同じタイミングで動くように）

    if gopro_recording == False:
        gopro_recording = True
        #record
        
        for o in gopro_dict.keys():
            cm.record(o,1)

        dpg.configure_item("Record_button_main",label="STOP!!")
    else:
        gopro_recording = False
        #stop recording
        for o in gopro_dict.keys():
            cm.record(o,0)

        dpg.configure_item("Record_button_main",label="Record!!")

    return gopro_recording


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

    dpg.add_button(label="Record!!",tag='Record_button_main',callback=recording,width=300, height=100)

def beep():
    print('beep')

def copy_files(sender, app_data, user_data):

    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    m = temp_files_dict[user_data]

    print ('media--\n',m)


def send_map(sender, app_data, user_data):

    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    cm.command_send(user_data,'beep_mute')
    cm.command_send(user_data,'beep')

    #m = cm.ret_all_media(url=user_data)

    #print ('media',m)


def add_button_gopros(parent):

    global temp_popro_ui_dict
    global gopro_dict

    temp_popro_ui_dict['gopro_single_buttons'] = []

    #print ('add_button_gopros')

    total_dict = {}

    for o in gopro_dict.keys():

        print ('gopro_single_buttons',o)

        tag = ret_uitag(o,gopro_dict[o]['name'])
        temp_popro_ui_dict['gopro_single_buttons'].append(tag)

        print ('tag---',tag)

        label = gopro_dict[o]['name'].replace(' ','\n')

        dpg.add_button(label=label,parent=parent,tag=temp_popro_ui_dict['gopro_single_buttons'][-1],callback=send_map,user_data=o,width=75, height=100)


#撮影したfileのpairを見つけて取得ボタンとして表示
def add_button_files(parent):


    print ('\n\n\n■--------add_button_files')

    global temp_popro_ui_dict
    global gopro_dict

    global temp_files_dict

    temp_files_dict = {}

    ####

    temp_popro_ui_dict['gopro_file_buttons'] = []

    #print ('add_button_gopros')

    #goproの台数
    lengopro = len(gopro_dict.keys())

    #一台以下だと何もしない私
    if lengopro < 2:
        return

    print ('----find gopros = ',lengopro)
    #全てのgoproのfileをdictで取得

    #最初の一台
    total_media_dict_main = cm.ret_all_media(url=list(gopro_dict.keys())[0])
    
    total_media_dict = {}

    cre_compi = 2
    dur_compi = 5

    for o in list(gopro_dict.keys())[1:]:

        print ('gopro_file_buttons',o)

        total_media_dict[o] = cm.ret_all_media(url=o)

    print ('total_media_dictのkey',total_media_dict.keys())

    #invertするわ
    

    for o in sorted(list(total_media_dict_main.keys()),reverse=True):

        base_cre = total_media_dict_main[o]['cre']
        base_dur = total_media_dict_main[o]['dur']

        print ('-----同時に撮影されたものを探す＞＞＞',total_media_dict_main[o]['dl'])

        saiyo_list = [total_media_dict_main[o]]

        #saiyo_dictn[total_media_dict_main[o]['localtime']] = [total_media_dict_main]

        for on in total_media_dict.keys():

            #http://172.20.195.51:8080
            print ('total_media_dict',on)

            kouho_dict = {}

            min = 0

            #全てのfileを比較
            for onn in total_media_dict[on]:
                #file単位の辞書
                #1710861484: {'n': 'GX010001.MP4', 'cre': '1710861484', 'mod': '1710861484', 'glrv': '710050', 'ls': '-1', 's': '12665667', 'localtime': '2024-03-20 00:18:04', 'dir': '100GOPRO', 'dur': '9', 'c': '0', 'avc_profile': '255', 'profile': '255', 'tag_count': 0, 'tags': [], 'w': '3840', 'h': '2160', 'fps': '30000', 'fps_denom': '1001', 'prog': '1', 'subsample': '0', 'dl': 'http://172.22.148.51:8080/videos/DCIM/100GOPRO/GX010001.MP4'}

                now_cre = total_media_dict[on][onn]['cre']
                #now_dur = total_media_dict[on][onn]['dur']



                print (base_cre,':',now_cre,total_media_dict[on][onn]['dl'])
                sa = abs(int(base_cre) - int(now_cre))

                if sa <= cre_compi:
                    print ('cre',sa)

                    dictn = dict(total_media_dict[on][onn])
                    dictn['gopro'] = on

                    kouho_dict[sa] = dictn

                ###'cre': '1710861484' が最も近くて、かつ２以内のもの、かつ、'dur'の差が5以内のものを取得
                #両方が成り立つものが二つ以上はないはず
        
            print ('\n\n■---kouho find----',len(kouho_dict.keys()))

            print ('kouho_dict',kouho_dict)

            if len(kouho_dict.keys()) > 0:

                #かつ、'dur'の差が5以内のものを取得

                u = dict(kouho_dict[sorted(list(kouho_dict.keys()))[0]])
                        
                print ('---u↓\n',u)        
                print ('kouho is',u['dur'])

                sa = abs(int(base_dur) - int(u['dur']))

                print ('***---sa as',sa)

                if sa <= dur_compi:
                    print ('dur as ',sa)

                    saiyo_list.append(u)


        ####
        print ('\n\n-----kokode______saiyo_list',saiyo_list)


        if len(saiyo_list) == lengopro:
        
            mp4s = []
            for s in saiyo_list:

                #print ('----s',s)
                mp4s.append(s)

            label = total_media_dict_main[o]['localtime']
            temp_files_dict[label] = mp4s

            
            dpg.add_button(label=label,parent=parent,callback=copy_files,user_data=label,width=200, height=15)



def add_button_command(parant,command):

    pass


def main():
    global gopro_dict
    gopro_dict = cm.ret_gopros()

    dpg.create_context()
    dpg.create_viewport()
    dpg.setup_dearpygui()

    with dpg.window(label="Example Window"):
        dpg.add_text("GoPro File explorer")
        #dpg.add_button(label="Save", callback=save_callback)
        #dpg.add_input_text(label="string")
        #dpg.add_slider_float(label="float")
        #add_ui_test()

        with dpg.menu_bar():
            dpg.add_menu(label="Menu Options")

        with dpg.child_window(autosize_x=True, height=100):
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

        with dpg.child_window(autosize_x=True,width=500, height=500):
            with dpg.group(horizontal=True, width=0):

                with dpg.child_window(width=500, height=500):
                    #撮影したfileのpairを見つけて取得ボタンとして表示
                    parent=dpg.last_item()
                    add_button_files(parent)

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

