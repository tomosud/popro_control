import re
import shutil
import dearpygui.dearpygui as dpg

from urllib.parse import urlparse
import popro_command as cm
import uuid
import os
import webbrowser

import popro_para_http as ph
import popro_camera_server_control as psc

import time
from urllib.parse import urlparse
import threading

#import popro_remote as prt

folder_path_base = 'C:/GoPro/'

global_ini = folder_path_base + 'Rename_Setting.ini'

gopro_dict = {}
temp_popro_ui_dict = {}

temp_files_dict = {}

#カメラの録画状態の保存
info_dict_past= {}


gopro_recording = False

#各日付フォルダにfileのrenameの関連付けを保存するjsonと同期して使う
global_file_rename_dict = {}

global_file_rename_dict = cm.load_settings(file_name=global_ini)

copying = 0

if 'add_filepath' not in global_file_rename_dict.keys():
    global_file_rename_dict['add_filepath'] = ''

#commandサーバーのアドレスを設定
if 'Commend_server' in global_file_rename_dict.keys():
    psc.set_server_url(global_file_rename_dict['Commend_server'])

def ret_uitag(name_str,memo):

    global temp_popro_ui_dict

    uuidnow = str(uuid.uuid4())

    temp_popro_ui_dict[uuidnow] = {'name':name_str,'memo':memo}

    return uuidnow

# command.py

'''

def print_this():
    print("Command function is called.")
    
    r = requests.get('https://www.yahoo.co.jp/')
    print(r.content)

'''


def get_base_url(url):
    # URLを解析する
    parsed_url = urlparse(url)
    # スキーム、ネットロケーション（IPやドメイン）、ポートを組み合わせてベースURLを作成する
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

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
    #print_this()

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

#再利用するので関数化。file buttonのDl情報を取得できる関数
#user_dataは代表のtime stamp/ dl pathに使う
def ret_dlpath_from_dict(dictn,time_stamp):

    #print ('ret_dlpath_from_dict',time_stamp,dictn)
    #print ('\n')

    ret = {}

    # URLの解析
    parsed_url = urlparse(dictn['dl'])
    # スキーム、ネットロケーション（ホストとポート）を結合して接続先のURLを生成
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    #goproの名前？
    gopro_name = gopro_dict[base_url]['name'].replace('_','')

    time_st = time_stamp.replace(' ','_').replace(':','_').replace('-','_')
    day = time_st.split('_')[0] + '_' + time_st.split('_')[1] + '_' + time_st.split('_')[2]

    #folder_path = folder_path_base + time_stamp.replace(' ','_').replace(':','_').replace('-','_')

    folder_path = folder_path_base + '/' + day + '/' + time_st

    #print ('Download-----',dictn['dl'],folder_path)

    url = dictn['dl']

    file_name = gopro_name + '_' + url.split('/')[-1]

    #print ('-----',file_name)

    ret['url'] = url
    ret['file_name'] = file_name
    ret['folder_path'] = folder_path

    return ret

#takeにdeleteと記述された場合mp4を削除するtest
def delete_files(button_id,deletemedias):

    global copying

    print('\ndelete flow!!')
    print(f"button id: {button_id}")

    copying = 1

    with dpg.theme() as red_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定（ここでは赤色）
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 32, 255))

    dpg.bind_item_theme(button_id, red_theme)

    #http://172.20.195.51:8080/videos/DCIM/100GOPRO/GX010736.MP4
    #http://10.5.5.9:8080/gopro/media/delete/file?path=105GOPRO/GOPR6879.JPG

    delete_urls = []

    for o in deletemedias:

        baseurl = get_base_url(o)
        
        sep = o.split('/')

        delete_url = baseurl + '/gopro/media/delete/file?path=' + sep[-2] + '/' + sep[-1]
        #print ('delete',o)
        print ('delete_url',delete_url)

        delete_urls.append(delete_url)
        cm.delete_file(delete_url)


    #groupごと非表示
    #dpg.delete_item(temp_popro_ui_dict['gopro_file_buttons_group'][button_id])

    dpg.configure_item(temp_popro_ui_dict['gopro_file_buttons_group'][button_id], show=False)

    copying = 0
    pass


def copy_files(sender, app_data, user_data):

    print(f"sender is button id: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")


    global copying
    
    #多重にcopyしないために
    if copying == 1:
        #
        print ('!今はCopy中なので受け付けない')
        return 0
    
    #button idからtext idを取得
    tex_id = temp_popro_ui_dict['gopro_file_buttons_textfield'][sender]
    takename = dpg.get_value(tex_id)

    m = temp_files_dict[user_data]

    #
    #m is list

    if takename.lower() == 'delete':
        #print ('media--\n',m)
        deletemedias = []
        for o in m:
            deletemedias.append(o['dl'])
        
        delete_files(sender,deletemedias)

        return 0


    copying = 1

    with dpg.theme() as red_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定（ここでは赤色）
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 32, 32, 255))

    dpg.bind_item_theme(sender, red_theme)



    url_dict = {}

    appnd_savepath = ''

    #処理時間を計測する
    start_time = time.time()  # 開始時間を記録

    for o in m:

        #print('o',o)

        #'gopro': 'http://172.20.195.51:8080' #これを求めたい
        #dl = http://172.22.148.51:8080/videos/DCIM/100GOPRO/GX010004.MP4'}
     

        rdictn = ret_dlpath_from_dict(o,user_data)

        #cm.download_file(url=rdictn['url'], file_name=rdictn['file_name'],folder_path=rdictn['folder_path'])

        #print ('-----Done!')
        appnd_savepath=rdictn['folder_path']
        url_dict[rdictn['url']] = rdictn['file_name']

    if not os.path.exists(appnd_savepath):
        os.makedirs(appnd_savepath)

    #非同期DLは失敗多いので廃止してたけど再開
    ph.download_main_wrapper(url_dict=url_dict,appnd_savepath=appnd_savepath)
    #cm.download_files_ThreadPoolExecutor(urls_and_filenames=url_dict, folder_path=appnd_savepath)

    print ('-----Finish!',user_data)

    #takeの名前でcopy
    #uuid = str(uuid.uuid4())



    d = cm.copy_to_take_name(appnd_savepath,takename)
    #不要　廃止
    
    #cm.write_list_to_file([takename],d + 'take_names.txt')

    #ここでで接続しなおす
    psc.connect_all_cameras(try_to_connect = True)

    end_time = time.time()  # 終了時間を記録
    elapsed_time = end_time - start_time  # 経過時間を計算
    print(f"--------GoproからのCopy 処理時間: {elapsed_time} 秒")    

    if global_file_rename_dict['add_filepath'] != '':

        #d C:/GoPro//2024_04_08/take_12-27_08/
        day = d.split('/')[-3]

        if cm.exist_addpath(serverpath=global_file_rename_dict['add_filepath']):
            # os.path.joinを使用してパスを組み立て
            addsavepath = os.path.join(global_file_rename_dict['add_filepath'], day)
            addsavepath = os.path.join(addsavepath,takename)

            print('-------add_filepath copy', d, addsavepath)
            
            gopro_button_color_update('dummy',work='copying_add',all=True,who='add copy')

            # shutil.copytreeを使用してディレクトリをコピー
            # コピー先のディレクトリが既に存在してもエラーを発生させずに処理を進める
            shutil.copytree(d, addsavepath, dirs_exist_ok=True)

    button_file_color_update()
    
    gopro_button_color_update('dummy',work='base',all=True,who='copy end')

    copying = o

    end_time = time.time()  # 終了時間を記録
    elapsed_timeb = end_time - start_time  # 経過時間を計算
    print(f"---------FileServerへのCopy 処理時間: {elapsed_timeb - elapsed_time} 秒")     
    print('---Copyは終了した。')      

def send_map(sender, app_data, user_data):

    print(f"sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    cm.command_send(user_data,'beep_mute')
    cm.command_send(user_data,'beep')

    #m = cm.ret_all_media(url=user_data)

    #print ('media',m)
    #print ('gopro_dict')
    #print (gopro_dict)

'''
def btest():
    urlbase = 'http://172.25.113.51:8080/gopro/camera/get_date_time'
    gopro_button_color_update(urlbase,work='base')
'''

def gopro_button_color_update(urlbase,work='base',all=False,who='me'):
    
    #名前で指定された場合はgopro_dictからurlを取得
    if 'http://' not in urlbase:
        for o in gopro_dict.keys():
            #print (gopro_dict)
            #よくない仕様　表記がぶれているので数字を取得する
            nanb1 = gopro_degit_from_name(gopro_dict[o]['name'])
            nanb2 = gopro_degit_from_name(urlbase)
            #print ('gopronanber---',gopro_dict[o]['name'],nanb1,nanb2,urlbase)
            if nanb1 == nanb2:
                urlbase = o

    #print ('---color chenge to ',work,' from ',who)

    global temp_popro_ui_dict

        # テーマを作成
    with dpg.theme() as gopro_button_base:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定
            dpg.add_theme_color(dpg.mvThemeCol_Button, (60,60,60, 255))
    with dpg.theme() as gopro_button_copying_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定
            dpg.add_theme_color(dpg.mvThemeCol_Button, (255,200,32, 255))
    with dpg.theme() as gopro_button_copying_add_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定
            dpg.add_theme_color(dpg.mvThemeCol_Button, (128,32, 32, 255))
    with dpg.theme() as gopro_button_recording_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定
            dpg.add_theme_color(dpg.mvThemeCol_Button, (200,32, 32, 255))

    dictn = temp_popro_ui_dict['gopro_single_buttons_ip_to_tag']

    runall = []

    if all:
        for o in dictn.keys():
            runall.append(o)
    else:

        runall = [urlbase]

    for o in runall:

        ip = get_base_url(o)

        if ip not in dictn.keys():
            print ('no entry dictn',ip)
            return 

    
        uiid = dictn[ip]
        
        if work == 'base':
            dpg.bind_item_theme(uiid, gopro_button_base)
        
        elif work == 'copying':
            dpg.bind_item_theme(uiid, gopro_button_copying_theme)

        elif work == 'copying_add':
            dpg.bind_item_theme(uiid, gopro_button_copying_add_theme)

        elif work == 'recording':
            dpg.bind_item_theme(uiid, gopro_button_recording_theme)

def add_button_gopros(parent):

    global temp_popro_ui_dict
    global gopro_dict

    #goproのボタンのuiのtagを保存するためのlist
    temp_popro_ui_dict['gopro_single_buttons'] = []

    #goproのipをkeyに、ボタンのuiのtagを保存するためのdict
    temp_popro_ui_dict['gopro_single_buttons_ip_to_tag'] = {}

    #print ('add_button_gopros')

    total_dict = {}

    for o in gopro_dict.keys():

        #print ('gopro_single_buttons',o)

        tag = ret_uitag(o,gopro_dict[o]['name'])
        temp_popro_ui_dict['gopro_single_buttons'].append(tag)

        #print ('\n---gopro_single_buttons tag---',tag)
        #print (o,gopro_dict[o]['name'])

        temp_popro_ui_dict['gopro_single_buttons_ip_to_tag'][o] = tag

        label = gopro_dict[o]['name'].replace(' ','\n')

        dpg.add_button(label=label,parent=parent,tag=temp_popro_ui_dict['gopro_single_buttons'][-1],callback=send_map,user_data=o,width=62, height=40)

    gopro_button_color_update(o,work='base',who='add buton')

def reload_file():
    
    print ('reload_file')
    
    #temp_popro_ui_dict['gopro_file_buttons_parant'] = parant

    if 'gopro_file_buttons_parent' in temp_popro_ui_dict.keys():
        pass
    else:
        print ('no entry gopro_file_buttons_parent')
        return 

    children = dpg.get_item_children(temp_popro_ui_dict['gopro_file_buttons_parent'])

    #print ('----children',children)
    #----children {0: [], 1: [38, 39, 40, 41], 2: [], 3: []}
    
    # 子アイテムの中で指定された名前を持つitemを削除
    for child_id in children[1]:
        #if dpg.get_item_label(child_id) == button_name_to_delete:
        dpg.delete_item(child_id)
        print ('delete',child_id)
    
    #入れ直し
    add_button_files(temp_popro_ui_dict['gopro_file_buttons_parent'])

    #時計を一致
    cm.get_time()    

def button_file_color_update():

    all_folders = []

    global temp_popro_ui_dict

    global global_file_rename_dict

    #global_file_rename_dict = cm.load_settings(file_name=global_ini)

    #存在によって色を変える

    # テーマを作成
    with dpg.theme() as orange_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定（ここでは赤色）
            dpg.add_theme_color(dpg.mvThemeCol_Button, (128, 64, 0, 255))

    with dpg.theme() as blue_theme:
        with dpg.theme_component(dpg.mvButton):
            # ボタンの背景色を設定（ここでは赤色）
            dpg.add_theme_color(dpg.mvThemeCol_Button, (32, 32, 32, 255))

    for o in temp_popro_ui_dict['gopro_file_buttons'].keys():
        #o is button's ui id

        files = []
        exsist = 0
        #gopro台数分のfileのdict
        m = temp_files_dict[temp_popro_ui_dict['gopro_file_buttons'][o]]

        # IDからuser_dataを取得 timestamp
        user_data = dpg.get_item_user_data(o)

        fldername = ret_dlpath_from_dict(m[0],user_data)['folder_path'].split('/')[-1]

        for on in m:

            rdictn = ret_dlpath_from_dict(on,user_data)
            
            file = rdictn['folder_path'] + '/' + rdictn['file_name']

            #print ('rdictn-----',rdictn)

            files.append(file)

            if os.path.exists(file):
                exsist += 1
        #filesはすべて存在してるか？
                

        if len(files) == exsist:
            dpg.bind_item_theme(o, blue_theme)
        else:
            dpg.bind_item_theme(o, orange_theme)

        texid = temp_popro_ui_dict['gopro_file_buttons_textfield'][o]

        #print ('fldername is ',fldername)

        if fldername in global_file_rename_dict.keys():
            dpg.set_value(texid, global_file_rename_dict[fldername])

        all_folders.append(fldername)

    #すでに存在しないfolderのkeyを削除
    #ただし、add_filepathのkeyは削除しない

    #ここ良くない仕様　keyの種類が増えると毎回足さないといけない
    dictn = {'add_filepath': global_file_rename_dict['add_filepath']}

    if 'Commend_server' in global_file_rename_dict.keys():
        dictn['Commend_server'] = global_file_rename_dict['Commend_server']

    for o in global_file_rename_dict.keys():

        if o in all_folders:
            dictn[o] = global_file_rename_dict[o]

    global_file_rename_dict = dict(dictn)

    cm.save_settings(global_file_rename_dict, file_name=global_ini)


#撮影したfileのpairを見つけて取得ボタンとして表示
def add_button_files(parent):

    #print ('\n\n\n■--------add_button_files')

    global temp_popro_ui_dict
    global gopro_dict

    global temp_files_dict

    temp_files_dict = {}

    ####
    #あとでbuttonにアクセスして色変えたりするため
    temp_popro_ui_dict['gopro_file_buttons'] = {}

    #あとでbuttonにアクセスして色変えたりするため
    temp_popro_ui_dict['gopro_file_buttons_textfield'] = {} 

    #削除用にbuttonのidとgroupを紐づけておく
    temp_popro_ui_dict['gopro_file_buttons_group'] = {} 

    #print ('add_button_gopros')

    #goproの台数
    lengopro = len(gopro_dict.keys())

    #一台以下だと何もしない私
    if lengopro < 2:
        return

    print ('----find gopros = ',lengopro)
    #全てのgoproのfileをdictで取得
    cre_compi = 5
    dur_compi = 3
    #dur_compi = 5

    ###
    alldic = cm.ret_all_media_palla(urls=list(gopro_dict.keys()))

    '''
    if alldic == None:
        #取得に失敗　再チャレンジ
        print ('取得に失敗 再チャレンジ')

        psc.connect_all_cameras(try_to_connect = True)
        add_button_files(parent)
    '''

    #print ('alldic',alldic)

    #最初の一台
    k1 = list(alldic.keys())[0]
    total_media_dict_main = alldic[k1]

    #print ('total_media_dict_main',total_media_dict_main)

    #最初の一台
    #total_media_dict_main = cm.ret_all_media(url=list(gopro_dict.keys())[0])
    
    #それ以外
    total_media_dict = {}

    for o in list(alldic.keys())[1:]:

        #print ('gopro_file_buttons',o)

        total_media_dict[o] = alldic[o]

    '''
    for o in list(gopro_dict.keys())[1:]:

        print ('gopro_file_buttons',o)

        total_media_dict[o] = cm.ret_all_media(url=o)
    '''

    #total_media_dict = cm.ret_all_media_palla(urls=list(gopro_dict.keys())[1:])

    #print ('total_media_dictのkey',total_media_dict.keys())

    #invertするわ
    
    for o in sorted(list(total_media_dict_main.keys()),reverse=True):

        base_cre = total_media_dict_main[o]['cre']
        base_dur = total_media_dict_main[o]['dur']

        #print ('-----同時に撮影されたものを探す＞＞＞',total_media_dict_main[o]['dl'])

        saiyo_list = [total_media_dict_main[o]]

        #saiyo_dictn[total_media_dict_main[o]['localtime']] = [total_media_dict_main]

        for on in total_media_dict.keys():

            #http://172.20.195.51:8080
            #print ('total_media_dict',on)

            kouho_dict = {}

            min = 0

            if total_media_dict[on] == None:
                #取得に失敗　再チャレンジ
                

                psc.connect_all_cameras(try_to_connect = True)
                raise ValueError("取得に失敗")
                #pause
                #time.sleep(2)

                #add_button_files(parent)

            #全てのfileを比較
            for onn in total_media_dict[on]:
                #file単位の辞書
                #1710861484: {'n': 'GX010001.MP4', 'cre': '1710861484', 'mod': '1710861484', 'glrv': '710050', 'ls': '-1', 's': '12665667', 'localtime': '2024-03-20 00:18:04', 'dir': '100GOPRO', 'dur': '9', 'c': '0', 'avc_profile': '255', 'profile': '255', 'tag_count': 0, 'tags': [], 'w': '3840', 'h': '2160', 'fps': '30000', 'fps_denom': '1001', 'prog': '1', 'subsample': '0', 'dl': 'http://172.22.148.51:8080/videos/DCIM/100GOPRO/GX010001.MP4'}

                now_cre = total_media_dict[on][onn]['cre']
                #now_dur = total_media_dict[on][onn]['dur']

                #print (base_cre,':',now_cre,total_media_dict[on][onn]['dl'])
                sa = abs(int(base_cre) - int(now_cre))

                if sa <= cre_compi:
                    #print ('cre',sa)

                    dictn = dict(total_media_dict[on][onn])
                    dictn['gopro'] = on

                    kouho_dict[sa] = dictn

                ###'cre': '1710861484' が最も近くて、かつ２以内のもの、かつ、'dur'の差が5以内のものを取得
                #両方が成り立つものが二つ以上はないはず
        
            #print ('\n\n■---kouho find----',len(kouho_dict.keys()))

            #print ('kouho_dict',kouho_dict)

            if len(kouho_dict.keys()) > 0:

                #かつ、'dur'の差が5以内のものを取得

                u = dict(kouho_dict[sorted(list(kouho_dict.keys()))[0]])
                        
                #print ('---u↓\n',u)        
                #print ('kouho is',u['dur'])

                sa = abs(int(base_dur) - int(u['dur']))

                #print ('***---sa as',sa)

                if sa <= dur_compi:
                    #print ('dur as ',sa)

                    saiyo_list.append(u)


        ####
        #print ('\n\n-----kokode______saiyo_list',saiyo_list)


        if len(saiyo_list) == lengopro:
        
            mp4s = []
            for s in saiyo_list:

                #print ('----s',s)
                mp4s.append(s)

            label = total_media_dict_main[o]['localtime'] + ' : ' + total_media_dict_main[o]['dur'] + 'sec'

            #yearはいらない
            label = '/'.join(label.split('-')[1:])

            temp_files_dict[total_media_dict_main[o]['localtime']] = mp4s

            #削除用にbuttonのidとgroupを紐づけておく
            grouptag = ret_uitag('temp','temp')
            #temp_popro_ui_dict['gopro_single_buttons'].append(tag)

            with dpg.group(tag=grouptag,horizontal=True,parent=parent):
            

                id = dpg.add_button(label=label,callback=copy_files,user_data=total_media_dict_main[o]['localtime'],width=160, height=15)

                #削除用にbuttonのidとgroupを紐づけておく
                temp_popro_ui_dict['gopro_file_buttons_group'][id] = grouptag

                #2024_04_03_21_16_09 時間を抽出 total_media_dict_main[o]['localtime']
                sept = (total_media_dict_main[o]['localtime'].replace(' ','_').replace(':','_').replace('-','_')).split('_')
                text_defo = 'take_' + sept[3] + '-' + sept[4] + '_' + sept[5]

                #rename　書き換えたら辞書も書き換える
                tex_id = dpg.add_input_text(label=":",user_data=total_media_dict_main[o]['localtime'], default_value=text_defo,callback=rename_setting,width=230, height=15)

                kz = 1

                #previe buttonをgoproの番号順に


                # ソートするために辞書のアイテムをリストに変換し、内側の辞書の'age'キーでソート
                sorted_items = sorted(gopro_dict.items(), key=lambda item: item[1]['name'])
                # ソートされたアイテムから新しい辞書を作成
                sorted_gopro_dict = {item[0]: item[1] for item in sorted_items}
                

                for onnn in sorted_gopro_dict.keys():

                    #print ('--gopro_dict---onn',gopro_dict[onnn]['name'],gopro_dict[onnn]['url'])

                    for onn in mp4s:

                        parsed_url = urlparse(onn['dl'])
                        # スキーム、ネットロケーション（ホストとポート）を結合して接続先のURLを生成
                        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                        if base_url == gopro_dict[onnn]['url']:

                            #openurl = 'http://172.20.195.51:8080/videos/DCIM/100GOPRO/GX010026.MP4'

                            #print ('--mp4s---onn',onn)

                            openurl = onn['dl']

                            dpg.add_button(label=str(kz),callback=open_url,user_data=openurl,width=15, height=15)

                            kz += 1

                #あとで色変えとかに使う
                temp_popro_ui_dict['gopro_file_buttons'][id] = total_media_dict_main[o]['localtime']

                #temp_popro_ui_dict['gopro_file_buttons_textfield']['tex_id'] = id

                temp_popro_ui_dict['gopro_file_buttons_textfield'][id] = tex_id
        '''
        else:
            #
            print ('-棄却　no match')
            print ('saiyo_list',len(saiyo_list))
            for o in saiyo_list:
                print (o)
        '''

    temp_popro_ui_dict['gopro_file_buttons_parent'] = parent

    button_file_color_update()

def open_url(sender, app_data, user_data): #mp4のurlを開く

    #import webbrowser

    url = user_data

    webbrowser.open(url)


def rename_setting(sender, app_data, user_data):

    print(f"rename_setting :: sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    #print ('rename_setting',user_data)

    #global_file_rename_dict

    global global_file_rename_dict

    setting_dict = dict(global_file_rename_dict)


    timestamp_underbar = user_data.replace(' ','_').replace(':','_').replace('-','_')

    setting_dict[timestamp_underbar] = app_data

    global_file_rename_dict = dict(setting_dict)


    #global_file_rename_dict[user_data] = app_data

    #print ('global_file_rename_dict',global_file_rename_dict)

    #print ('rename_setting',app

    cm.save_settings(setting_dict, file_name=global_ini)


def add_button_command(parant,command):

    pass

def addpath_setting(sender, app_data, user_data):

    print(f"rename_setting :: sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")

    global global_file_rename_dict

    if app_data == '':
        global_file_rename_dict['add_filepath'] = app_data
        setting_dict = dict(global_file_rename_dict)
        cm.save_settings(setting_dict, file_name=global_ini)

    if cm.exist_addpath(serverpath=app_data):

        print (app_data)

        app_data = app_data.replace('\\','/')
        if app_data[-1] == '/':
            app_data = app_data[:-1]

        global_file_rename_dict['add_filepath'] = app_data
        setting_dict = dict(global_file_rename_dict)
        cm.save_settings(setting_dict, file_name=global_ini)

    else:
        print ('not exist')

#settingに内容を保存する汎用的な関数
#user_settingでkeyと、内容の一致確認のlistを設定する　
# 'Commend_server',['http://',':'] 
def setting_save_any(sender, app_data, user_data):

    global global_file_rename_dict

    print(f"rename_setting :: sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is url as: {user_data}")


    if app_data != '':

        flg = 0

        for o in user_data[1]:

            if o not in app_data:
                flg = flg + 1
                print ('not in',o,flg)

        if flg == 0 and '*' not in app_data:

            print ('setting_save_any:',app_data)

            global_file_rename_dict[user_data[0]] = app_data
            setting_dict = dict(global_file_rename_dict)
            cm.save_settings(setting_dict, file_name=global_ini)

    '''
    global global_file_rename_dict

    if app_data == '':
        global_file_rename_dict['add_filepath'] = app_data
        setting_dict = dict(global_file_rename_dict)
        cm.save_settings(setting_dict, file_name=global_ini)


    '''
    #cm.save_settings(setting_dict, file_name=global_ini)

def openpath(sender, app_data, user_data):
    print(f"rename_setting :: sender is: {sender}")
    print(f"app_data is: {app_data}")
    print(f"user_data is : {user_data}")

    path = ''
    if user_data == 'Additional save path':
        if 'add_filepath' in global_file_rename_dict.keys():
            if global_file_rename_dict['add_filepath'] != '':
                path = global_file_rename_dict['add_filepath'].replace('/','\\')
                #network pathは\で区切る
                

    
    elif user_data == 'local temp':
        path = 'C:/GoPro/'

        #dir無ければ作る
        if not os.path.exists(path):
            os.makedirs(path)

    if path != '':
        #エクスプローラーでフォルダを開く
        os.startfile(path)

'''
def wol(sender, app_data, user_data):
    print('wol')

    cm.wol_all()


def close_popup(sender, app_data, user_data):
    print('close_popup')
    dpg.delete_item("popup_id")

def save_api_key(sender, app_data, user_data):

    key = dpg.get_value("api_key_input")

    print('save_api_key', key)

def setApiKey_remote(sender, app_data, user_data):
    print('setApiKey_remote')

    #popupでtextを入力させる

    # ポップアップウィンドウを作成
    with dpg.popup(id="popup_id", modal=True, mousebutton=1, width=300, height=100, on_close=close_popup):
        # ポップアップウィンドウ内にテキスト入力ボックスを作成
        dpg.add_input_text(label="API Key", hint="Enter API Key", width=200, height=20, id="api_key_input")
        # ポップアップウィンドウ内にボタンを作成
        dpg.add_button(label="OK", callback=save_api_key, width=100, height=30)
'''
def get_cyclic_value(my_list, index):
    # リストの個数で剰余を取ることで、indexがリストの範囲を超えないようにする
    cyclic_index = index % len(my_list)
    return my_list[cyclic_index]

# タイマー関数
def timer_with_function(seconds):

    gopros =  list(gopro_dict.keys())

    print ('-----------',gopros,len(gopros))

    kz = 0

    if seconds <= 2:
        seconds = 2

    for i in range(seconds-1):
        #function_a()  # 1秒ごとに関数Aを実行
        time.sleep(1)  # 1秒待機

        if len(gopros) == 0:
            print ('no gopro')
        
        else:

            s = get_cyclic_value(gopros,kz)

            cm.command_send(s,'beep_mute')
            cm.command_send(s,'beep')

            s = get_cyclic_value(gopros,kz+1)
            time.sleep(0.2)

            cm.command_send(s,'beep_mute')
            cm.command_send(s,'beep')

        kz += 1

        print (kz,':',seconds)

    time.sleep(1)  # 1秒待機
    print(f"{seconds}秒経過しました")

    for o in gopros:
        cm.command_send(o,'beep_mute')
        cm.command_send(o,'beep')
    


def send_server_command(sender, app_data, user_data):

    send_server_command_do(user_data)

def send_server_command_do(user_data,debug = 0):


    #print(f"rename_setting :: sender is: {sender}")
    #print(f"app_data is: {app_data}")
    print(f"user_data is: {user_data}")

    
    #時計を一致
    #cm.get_time()
    #psc.connect_all_cameras(try_to_connect = True)
    #0.5秒待つ

    #time.sleep(0.5)

    if 'Commend_server' in global_file_rename_dict.keys(): #設定あれば
        #if psc.connect_all_cameras(try_to_connect = True): 
        psc.set_server_url(global_file_rename_dict['Commend_server'])

        if user_data[1] != 0:
            timer_with_function(user_data[1])

        if debug == 0:

            psc.send_camera_command(user_data[0])

    else:
        print ('no server setting')
        return

#同時に録画コマンドを送るtest
def record_test():

    #print (gopro_dict)
    url_list = []

    for o in gopro_dict.keys():
        url_list.append(o + '/gopro/camera/shutter/start')

    ph.execute_post(url_list)

def test_func(sender, app_data, user_data): 

    print (gopro_dict)
    


#send_camera_command('startRecording')

# カメラのステータスを2秒ごとに取得するスレッドで実行される関数
def update_camera_status_periodically():

    #time.sleep(5)
    global info_dict_past

    while True:

        info_dict = {}

        status = psc.get_status_all_cameras('')

        if 'cameras' not in status.keys():
            print("Error: Camera status could not be updated.")
        else:
        # 取得した辞書の内容をここで処理する

            #print("Camera status updated!:",len(status['cameras']),'cameras')

            for o in status['cameras']:
                #print(o['name'],o['bluetooth_status'])

                dictn = {}
                dictn['recording_time'] = '00h:00m:00s'
                dictn['camera_recording'] = False
                dictn['name'] = o['name']
                dictn['bluetooth_status'] = o['bluetooth_status']
                if o['bluetooth_status'] == 'connected':
                    dictn['recording_time'] = o['recording_time']
                    dictn['camera_recording'] = o['camera_recording']

                #print (dictn['name'],dictn['bluetooth_status'],dictn['camera_recording'],dictn['recording_time'])

                info_dict[o['name']] = dictn
             


            for o in info_dict.keys():

                flg = 0

                if o not in info_dict_past.keys():
                    flg = 1
                else:
                    if info_dict[o]['camera_recording'] != info_dict_past[o]['camera_recording']:

                        #print ('\n\nstatus chenged!! >> ',o,info_dict[o]['camera_recording'])

                        flg = 1

                if flg == 1 and copying == 0:

                    if info_dict[o]['camera_recording'] == True:
                        gopro_button_color_update(o,work='recording',who='recording')
                    else:
                        gopro_button_color_update(o,work='base',who='stoprecording')
             


        #前回の情報の保存
        info_dict_past = info_dict
        # 待つ
        time.sleep(3)

#HERO12 Black02 とかHERO12 Black2 (172.24.106.51)とか表記がぶれてるので数字を取り出す
def gopro_degit_from_name(name):

    name = name.replace(' ','').split('(')[0]

    match = re.search(r'(\d+)$', name)
    if match:
        return int(match.group(1))
    return None  # 数字が見つからなかった場合

def main():

    global gopro_dict
    gopro_dict = cm.ret_gopros()

    #接続を試みる
    psc.connect_all_cameras(try_to_connect = True)
    time.sleep(1)

    ui_width = 650

    dpg.create_context()
    # ビューポートのサイズを設定
    dpg.create_viewport(title="GoPro File explorer", width=ui_width+10, height=800)

    #dpg.create_viewport()
    dpg.setup_dearpygui()
    #width=1200, height=1000,no_close=True,pos=(0,0)

    with dpg.window(label="GoPro File explorer",width=ui_width, height=800,pos=(0,0),
                    no_title_bar=True,  # タイトルバーを非表示にする
                    no_move=True,       # ウィンドウの移動を禁止する
                    no_resize=True,     # ウィンドウのリサイズを禁止する
                    no_collapse=True,   # ウィンドウの折りたたみを禁止する
                    no_close=True):     # ウィンドウの閉じるボタンを無効にする       

        with dpg.group(horizontal=True):
             
            dpg.add_button(label='Additional save path:',user_data='Additional save path',callback=openpath,width=150, height=20)
            
            #dpg.add_input_text(label=":  ",default_value=global_file_rename_dict['add_filepath'],callback=addpath_setting,width=250, height=15)

            if len(global_file_rename_dict['add_filepath']) > 20:

                sepp = global_file_rename_dict['add_filepath'].split('/')

                dpg.add_text('/'.join(sepp[:4]) + '/.../' + sepp[-1])
            else:

                dpg.add_text(global_file_rename_dict['add_filepath'])

            dpg.add_button(label=':local temp path',user_data='local temp',callback=openpath,width=120, height=20)
            #dpg.add_button(label="Save", callback=save_callback)
            #dpg.add_input_text(label="string")
            #dpg.add_slider_float(label="float")
            #add_ui_test()

        with dpg.menu_bar():
            with dpg.menu(label="Menu"):
                #dpg.add_text("Wake up!!")
                #dpg.add_menu_item(label="Try", callback=wol)
                #dpg.add_text("Remote Control")
                #dpg.add_menu_item(label="Set API Key", callback=setApiKey_remote)

                #http://10.102.106.60:810

                with dpg.tree_node(label="Commend server"):
                    dpg.add_text("Set Camera Tools for Hero Commend server")
                    dpg.add_text("e.g. http://10.102.106.60:810")
                    dpg.add_separator()

                    deff_url = 'http://*.*.*.*:*'
                    
                    if 'Commend_server' in global_file_rename_dict.keys():
                        deff_url = global_file_rename_dict['Commend_server']


                    dpg.add_input_text(label="",user_data=['Commend_server',['http://','.',':']], default_value=deff_url,callback=setting_save_any,width=250, height=15)

                with dpg.tree_node(label="Additional SavePath"):
                                    dpg.add_text(r"Set additional file save path")
                                    dpg.add_text(r"e.g. \\*.*.*.*\***\Shared\Move_ai")
                                    dpg.add_separator()

                                    deff_url = r'\\*.*.*.*\***\Shared\Move_ai'
                                    
                                    if 'Commend_server' in global_file_rename_dict.keys():
                                        deff_url = global_file_rename_dict['add_filepath']

                                    dpg.add_input_text(label=":  ",default_value=deff_url,callback=addpath_setting,width=250, height=15)
                
                with dpg.tree_node(label="Utility"):
                    dpg.add_text("Othr Test functions and utilities")
                    dpg.add_button(label="Set/ ALL Cams Time Settings",callback=cm.get_time)
                    dpg.add_button(label="test_func",callback=test_func)

                    #btest()
                    dpg.add_separator()

        #record button
        #if psc.connect_all_cameras(try_to_connect = True): #全てのカメラに接続できたら
        if 'Commend_server' in global_file_rename_dict.keys(): #設定あれば
            if psc.connect_all_cameras(try_to_connect = True): #全てのカメラに接続できたら
                hn = 35

                with dpg.theme() as record_theme:
                    with dpg.theme_component(dpg.mvButton):
                        # ボタンの背景色を設定
                        dpg.add_theme_color(dpg.mvThemeCol_Button, (32,200,32, 255))
                with dpg.theme() as stop_theme:
                    with dpg.theme_component(dpg.mvButton):
                        # ボタンの背景色を設定
                        dpg.add_theme_color(dpg.mvThemeCol_Button, (200,32, 32, 255))
                
                recb = []
                with dpg.child_window(autosize_x=True, height=50):
                    with dpg.group(horizontal=True):

                        parent=dpg.last_item()
                        dpg.add_text("Rec:")
                        rb = dpg.add_button(label="Record\nALL", user_data=['startRecording',0],callback=send_server_command,width=150, height=hn)
                        recb.append(rb)
                        rb = dpg.add_button(label="Timer\n10sec",  user_data=['startRecording',10],callback=send_server_command,width=45, height=hn)
                        recb.append(rb)
                        rb = dpg.add_button(label="Timer\n8sec",  user_data=['startRecording',8],callback=send_server_command,width=45, height=hn)
                        recb.append(rb)
                        rb = dpg.add_button(label="Timer\n5sec",  user_data=['startRecording',5],callback=send_server_command,width=45, height=hn)
                        recb.append(rb)
                        rb = dpg.add_button(label="Timer\n3sec",  user_data=['startRecording',3],callback=send_server_command,width=45, height=hn)
                        recb.append(rb)

                        dpg.add_text("    :    \n    :    ")                   
                        st = dpg.add_button(label="STOP ALL",  user_data=['stopRecording',0],callback=send_server_command,width=75, height=hn)

                    for rb in recb:
                        dpg.bind_item_theme(rb, record_theme)

                    dpg.bind_item_theme(st, stop_theme)

        #gopros
        with dpg.child_window(autosize_x=True, height=55):
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


        with dpg.child_window(autosize_x=True,width=ui_width*0.9, height=50):
            with dpg.group(horizontal=True, width=0):
                dpg.add_button(label='Relaod Files',callback=reload_file,width=ui_width*0.85, height=20)

        with dpg.child_window(autosize_x=True,width=ui_width*0.9, height=500):
            with dpg.group(horizontal=True, width=0):

                with dpg.child_window(width=ui_width*0.95, height=500):
                    #撮影したfileのpairを見つけて取得ボタンとして表示
                    parent=dpg.last_item()
                    add_button_files(parent)

    # ビューポートのリサイズを無効化
    #dpg.set_viewport_resizable(False)

    #時計を一致
    cm.get_time()

    print (cm.get_network_interfaces())

    #cemera状態の監視
    print("start watch dog...")

    
    # 別スレッドでカメラステータスの定期的な更新を開始
    status_thread = threading.Thread(target=update_camera_status_periodically, args=())
    status_thread.daemon = True  # メインスレッド終了時にスレッドも終了
    status_thread.start()
    

    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

    #非同期でリモートコントロールを起動
    #prt.start_remote()

'''

def demoui():
    dpg.create_context()
    dpg.create_viewport(title='Custom Title', width=600, height=600)

    demo.show_demo()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
'''
#main() を実行 ファイルを起動した場合は

if __name__ == "__main__":
    main()
    #demoui()