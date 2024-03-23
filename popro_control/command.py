import requests
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # Python 3.9以降で利用可能




setting_dict = {'key1': 'value1', 'key2': 'value2'}

testurl = 'http://172.20.195.51:8080/gp/gpMediaList'

#以下をGoProの個体認証にも使う
testBaseurl = 'http://172.20.195.51:8080'

# URLからJSONデータを取得する関数
def get_json_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードが200以外の場合はエラーを発生させる
        return response.json()  # JSONデータをPythonの辞書に変換
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")
    except requests.exceptions.RequestException as e:
        print(f"リクエスト中にエラーが発生しました: {e}")
'''
{"id":"298554459323482383","media":[{"d":"100GOPRO","fs":[{"n":"GX010001.MP4","cre":"1710861484","mod":"1710861484","glrv":"834310","ls":"-1","s":"23898423"},{"n":"GOPR0002.JPG","cre":"1710861621","mod":"1710861621","s":"2969585"},{"n":"GX010003.MP4","cre":"1710861662","mod":"1710861662","glrv":"561217","ls":"-1","s":"6519470"},{"n":"GX010004.MP4","cre":"1710861671","mod":"1710861671","glrv":"351041","ls":"-1","s":"5432126"},{"n":"GX010005.MP4","cre":"1710865287","mod":"1710865287","glrv":"159814","ls":"-1","s":"4979566"},{"n":"GX010006.MP4","cre":"1710865744","mod":"1710865744","glrv":"1368524","ls":"-1","s":"13743412"},{"n":"GX010007.MP4","cre":"1710866831","mod":"1710866831","glrv":"284103","ls":"-1","s":"3891184"}]}]}
'''
#'http://172.20.195.51:8080/gp/gpMediaList'
def ret_all_media(url=testBaseurl):
    gurl = url + '/gp/gpMediaList'


    e = check_url(gurl)

    print ('------',e)

    if e[0] == False:
        print ('error:',e[1])
        return

    gjeson = get_json_data(gurl)

    #dir media
    data = {}

    #create timeでソートした辞書を作成

    for o  in gjeson['media']:
        #dirごとのlist
        dir = o['d']

        for on in o['fs']:

            #mp4のみ
            if on['n'].find('.MP4') > 0:

                #one is dict

                # Unixタイムスタンプ
                timestamp = int(on['cre'])

                #print ('unixtime',timestamp)
                # UTCでdatetimeオブジェクトを作成
                utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                # 日本時間（JST）に変換
                #jst_time = utc_time.astimezone(ZoneInfo("Asia/Tokyo"))

                # システムのローカルタイムゾーンを使用してローカル時間に変換
                local_time = utc_time.astimezone()

                
                #print("日本時間（JST）:", jst_time.strftime('%Y-%m-%d %H:%M:%S'))

                localtime = local_time.strftime('%Y-%m-%d %H:%M:%S')

                # 日本時間とローカル時間を文字列で表示
                print ('\n---',"dir:",dir, "name:",on['n'],' : ', localtime)

                on['localtime'] = localtime
                on['dir'] = dir

                #http://172.22.148.51:8080/videos/DCIM/100GOPRO/GX010001.MP4
                on['dl'] = url + '/videos/DCIM/' + dir + '/' + on['n']

                print(on['dl'])

                data[timestamp] = on

    return data



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

        with dpg.menu_bar():
            dpg.add_menu(label="Menu Options")
        with dpg.child_window(autosize_x=True, height=95):
            with dpg.group(horizontal=True):
                dpg.add_button(label="Header 1", width=75, height=75)
                dpg.add_button(label="Header 2", width=75, height=75)
                dpg.add_button(label="Header 3", width=75, height=75)
                dpg.add_button(label="Header 1", width=75, height=75)
                dpg.add_button(label="Header 2", width=75, height=75)                                            
        with dpg.child_window(autosize_x=True, height=175):
            with dpg.group(horizontal=True, width=0):
                with dpg.child_window(width=102, height=150):
                    with dpg.tree_node(label="Nav 1"):
                        dpg.add_button(label="Button 1")
                    with dpg.tree_node(label="Nav 2"):
                        dpg.add_button(label="Button 2")
                    with dpg.tree_node(label="Nav 3"):
                        dpg.add_button(label="Button 3")
                with dpg.child_window(width=300, height=150):
                    dpg.add_button(label="Button 1")
                    dpg.add_button(label="Button 2")
                    dpg.add_button(label="Button 3")
                with dpg.child_window(width=50, height=150):
                    dpg.add_button(label="B1", width=25, height=25)
                    dpg.add_button(label="B2", width=25, height=25)
                    dpg.add_button(label="B3", width=25, height=25)
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

def get(work=0):

    url = "http://172.20.195.51:8080/gp/gpMediaList"

    if work == 1:
        url = testurl
    elif work == 2:
        url = 'https://www.google.co.jp/'

    e = check_url(url)

    print ('------',e)

#get(0)
'''    
# JSONデータを取得し、特定の情報を抽出する例
url = "http://172.20.195.51:8080/gp/gpMediaList"
data = get_json_data(url)

for o in data.keys():
    print(o,data[o])
'''

#ret_all_media()

#ui()

demoui()