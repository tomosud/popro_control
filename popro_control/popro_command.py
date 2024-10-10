import requests
import os
import json
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo  # Python 3.9以降で利用可能
import time

import shutil
import glob
import pathlib

# 並列処理用
from concurrent.futures import ThreadPoolExecutor, as_completed

import pathlib
import psutil
import socket
import re

from wakeonlan import send_magic_packet



gopro_dict = {}

setting_dict = {'key1': 'value1', 'key2': 'value2'}
testurl = 'http://172.20.195.51:8080/gp/gpMediaList'
#以下をGoProの個体認証にも使う
testBaseurl = 'http://172.20.195.51:8080'

#ip_pattern = r'172\.2\d\.1\d{2}\.5\d'

#

def get_network_interfaces(pattern = r'172\.2\d\.1\d{2}\.5\d'):
    regex = re.compile(pattern)
    addrs = psutil.net_if_addrs()
    network_info = {}

    result = []

    for interface, addr_info in addrs.items():
        # 正規表現にマッチするIPv4アドレスのみをフィルタリングしてリストに格納
        addresses = [addr.address for addr in addr_info if addr.family == socket.AF_INET and regex.match(addr.address)]
        #addresses = [addr.address for addr in addr_info if addr.family == socket.AF_INET]
        if addresses:  # マッチするIPv4アドレスが存在する場合のみ保存
            #network_info[interface] = addresses

            ad = addresses[0]
            #172.26.186.54
            #172.26.186.51
            #末尾を1にする #見えてるipと実際のipが違う なぜ？

            ad = ad[:-1] + '1'

            result.append(ad)
    return result

def exist_addpath(serverpath=''):
    # パスのフォーマットを修正（\を/に置き換え）
    serverpath = serverpath.replace('\\', '/')

    # パスが空の場合は何もしない
    if serverpath == '':
        return None

    # パスが//で始まるか確認
    if not serverpath.startswith('//'):
        print("無効なネットワークパスです。パスは//で始まる必要があります。")
        return None

    # pathlibを使用してWindows形式のパスに変換
    # 先頭の//を\\に戻す
    formatted_path = pathlib.WindowsPath(r'\\' + serverpath[2:])

    # パスの存在確認
    if formatted_path.exists():
        print("指定のファイルもしくはディレクトリが存在しています。")
        # 指定パス以下のフォルダ、ファイルを列挙
        #print(list(formatted_path.glob('*')))

        return serverpath
    else:
        #print("指定のファイルもしくはディレクトリが存在していません。")

        return None

# 関数のテスト（サンプルパスを適切に置き換えて使用してください）
# exist_addpath('//servername/sharedfolder')



def download_files_ThreadPoolExecutor(urls_and_filenames, folder_path):
    # ThreadPoolExecutorを使って非同期ダウンロードを実行

    size = len(urls_and_filenames)

    with ThreadPoolExecutor(max_workers=size) as executor:
        # ダウンロードタスクの辞書を作成
        future_to_url = {executor.submit(download_file, url, file_name, folder_path): url for url, file_name in urls_and_filenames.items()}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # 結果（成功時のメッセージ）を取得
                future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))

def download_file(url, file_name, folder_path):
    # 指定されたフォルダが存在しない場合は作成
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # ファイルをダウンロードして保存するフルパスを構築
    file_path = os.path.join(folder_path, file_name).replace('\\', '/')
    
    print ('try file_path',file_path)


    # URLからファイルをダウンロード
    response = requests.get(url)
    
    # HTTPリクエストが成功したか確認
    if response.status_code == 200:
        # ファイルを書き込む
        with open(file_path, 'wb') as file:
            file.write(response.content)

        print(f'File has been downloaded and saved to {file_path}')
    else:
        print('Failed to download the file. Please check the URL or your internet connection.')


'''
# 使用例
url = 'http://172.20.195.51:8080/videos/DCIM/100GOPRO/GX010001.MP4'
folder_path = '/desired/path/to/save'
file_name = 'GX010001.MP4'

'''



def check_urls(url,timeout=5):

    #"http://172.20.195.51:8080/gp/gpMediaList"

    url = url + '/gp/gpMediaList'

    try:
        # タイムアウトを10秒に設定
        response = requests.get(url, timeout=timeout)
        if 200 <= response.status_code < 300:
            return True, response.status_code
        else:
            return False, response.status_code
    except requests.exceptions.RequestException as e:
        return False, str(e)


#接続できているGoProを返す
def ret_gopros(connect=True):

    global gopro_dict

    #goproのリストを返す

    '''
    data = ['HERO12 Black01(172.24.106.51)',
    'HERO12 Black02 (172.26.186.51)',
    'HERO12 Black03 (172.20.195.51)',
    'HERO12 Black04 (172.25.113.51)',
    'HERO12 Black05 (172.22.148.51)']
    '''

    #ipをkeyにした辞書を返す
    #'http://172.20.195.51:8080'

    #results = ret_json_data_palla(geturls) 

    ret = {}

    #iplist　実際に接続したipから取得するようにした
    data = get_network_interfaces()
    
    for o in data:
            
            #ip = o.split('(')[1].split(')')[0]

            ip = o

            if '172.' in ip:
                #usb
                ip = 'http://' + ip + ':8080'

                #
                dictn = {'url':ip}
                '''
                sep = o.split('(')[0].split(' ')
                dictn['name'] = sep[0] + ' ' + sep[1]
                '''
                
                k = ip + '/gopro/camera/info'
                r = get_json_data(k)
                print ('r',r)

                dictn['name'] = r['ap_ssid']
                dictn['checkurl'] = ip + '/gp/gpMediaList'

                #for WOL
                dictn['ap_mac_addr'] = r['ap_mac_addr']

                ret[ip] = dictn

            '''
            elif '10.5.5.9' in ip:
                #wifi
                ip = 'http://' + ip
            '''
                #未対応
    #print (ret)

    '''
    newret = {}

    if connect == True:

        urls = ret.keys()
            # 他のURLを追加

        print ('Start Check!-----urls',urls)

        # 成功したURLを格納するリスト
        successful_urls = []

        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_url = {executor.submit(check_urls, url): url for url in urls}
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    success, _ = future.result()
                    if success:
                        successful_urls.append(url)  # 成功したURLをリストに追加
                except Exception as exc:
                    # エラー処理（ここでは単にエラーメッセージを表示）
                    print(f"{url}: {exc}")

        # 成功したURLのリストを表示
        print("成功したURL:")
        for o in successful_urls:
            print(o)
            newret[o] = ret[o]

        gopro_dict = newret

        set_to_bacic_capture_mode()


        #keyをsort
        newret = dict(sorted(newret.items()))

        return newret
    '''

    gopro_dict = ret
    set_to_bacic_capture_mode()
    #keyをsort
    ret = dict(sorted(ret.items()))
    return ret

    '''
        # 最大12のスレッドを使用して並列処理
        with ThreadPoolExecutor(max_workers=12) as executor:
            # すべてのURLに対して関数を実行
            future_to_url = {executor.submit(check_urls, ret[url]['checkurl']): url for url in urls}
            # 結果を収集
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    print ('\nFind!!')
                    print(f"{url}: {result}")

                    newret[url] = ret[url]

                except Exception as exc:
                    print('Can not connect -- ',f"{url}: {exc}")
                    pass

        print ('----check end' ,newret)

    gopro_dict = newret

    return newret
    '''
    #return ret

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


# 並列処理を使用して複数のURLからjsonのデータを取得する関数
def ret_json_data_palla(urls):
    results = {}
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        # 各URLに対してret_all_media関数を非同期で実行するFutureを作成
        future_to_url = {executor.submit(get_json_data, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # Futureの結果を取得し、URLをキーとして結果の辞書に追加
                results[url] = future.result()
            except Exception as exc:
                print(f'URL {url} generated an exception: {exc}')
                results[url] = None  # エラーが発生した場合はNoneを割り当てる

    #keyをsort
    results = dict(sorted(results.items()))     

    return results


# 並列処理を使用して複数のURLからmediaのデータを取得する関数
def ret_all_media_palla(urls):
    results = {}
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        # 各URLに対してret_all_media関数を非同期で実行するFutureを作成
        future_to_url = {executor.submit(ret_all_media, url): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                # Futureの結果を取得し、URLをキーとして結果の辞書に追加
                results[url] = future.result()
            except Exception as exc:
                print(f'URL {url} generated an exception: {exc}')
                results[url] = None  # エラーが発生した場合はNoneを割り当てる

    #keyをsort
    results = dict(sorted(results.items()))     

    return results


def ret_all_media(url=testBaseurl):

    gurl = url + '/gp/gpMediaList'

    e = check_url_one(gurl)

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

                timestamp = timestamp - 32400  # 9時間分の秒数を引く

                #print ('unixtime',timestamp)
                # UTCでdatetimeオブジェクトを作成
                utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                # 日本時間（JST）に変換
                local_time = utc_time.astimezone(ZoneInfo("Asia/Tokyo"))

                # システムのローカルタイムゾーンを使用してローカル時間に変換
                #local_time = utc_time.astimezone()

                
                #print("日本時間（JST）:", jst_time.strftime('%Y-%m-%d %H:%M:%S'))

                localtime = local_time.strftime('%Y-%m-%d %H:%M:%S')



                on['localtime'] = localtime
                on['dir'] = dir

                #lengthほかも取得する
                #http://172.20.195.51:8080/gp/gpMediaMetadata?p=100GOPRO/GX010015.MP4&t=videoinfo

                infourl = url + '/gp/gpMediaMetadata?p=' + dir + '/' + on['n'] + '&t=videoinfo'

                info = get_json_data(infourl)

                #onに追加(update)
                on.update(info)


                #http://172.22.148.51:8080/videos/DCIM/100GOPRO/GX010001.MP4
                on['dl'] = url + '/videos/DCIM/' + dir + '/' + on['n']

                #print(on['dl'])

                data[timestamp] = on

                # 日本時間とローカル時間を文字列で表示
                #print ('\n---',"dir:",dir, "name:",on['n'],' : (9時間ずれてる？)日本時間（JST）', localtime, ' *dur:',on['dur'],' sec')                

    return data

def save_settings(setting_dict, file_name='tool_setting.ini'):

    #ファイルなければ作成　フォルダも
    if not os.path.exists(file_name):

        #フォルダも作成
        sep = file_name.split('/')
        path = '/'.join(sep[:-1])

        if not os.path.exists(path):
            os.makedirs(path)
            

    with open(file_name, 'w') as file:
        json.dump(setting_dict, file)

def load_settings(file_name='tool_setting.ini'):
    try:
        with open(file_name, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File '{file_name}' not found. Returning empty dictionary.")
        return {}

def check_url_one(url):
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
    
def set_to_bacic_capture_mode():

    for o in gopro_dict.keys():

        set_capture_mode(o)

def set_capture_mode(url):

    print ('set_capture_mode',url)
    command_send(url,'beep_mute')

    #command_send(url,'1080p')
    #command_send(url,'60fps')
    #command_send(url,'Shutter_Auto')
    command_send(url,'LED_ON')
    #command_send(url,'Lens_Linear')
    command_send(url,'Video_mode')
    #command_send(url,'Hypersmooth_OFF')
    #command_send(url,'Horizon Lock OFF')		

    #command_send(url,'beep')	

def command_send(url,type):

    #これらのコマンドは古そう　
    if type =='beep':
        url = url + '/gp/gpControl/setting/87/70'
    elif type == 'beep_mute':
        url = url + '/gp/gpControl/setting/87/0'       
    elif type == '1080p':
        url = url + '/gp/gpControl/setting/2/9'
    elif type == '60fps':
        url = url + '/gp/gpControl/setting/3/5'
    elif type == 'Shutter_Auto':
        url = url + '/gp/gpControl/setting/19/0'
    elif type == 'LED_ON':
        url = url + '/gp/gpControl/setting/91/2'
    elif type == 'Lens_Linear':
        url = url + '/gp/gpControl/setting/121/4'
    elif type == 'Video_mode':
        url = url + '/gp/gpControl/setting/128/13'
    elif type == 'Hypersmooth_OFF':
        url = url + '/gp/gpControl/setting/135/0'
    elif type == 'HiLight':
        url = url + '/gp/gpControl/setting/153/1'
    elif type == 'Horizon Lock OFF':
        url = url + '/gp/gpControl/setting/165/0'

    #

    try:
        response = requests.get(url, timeout=10)  # タイムアウトを10秒に設定
        if 200 <= response.status_code < 300:
            print("Request was successful.")
            # 応答内容を表示
            print(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


#あとでちゃんと書く
def record(url,on_off):

    '''
    Trigger: http://10.5.5.9/gp/gpControl/command/shutter?p=1
    Stop (Video/Timelapse): http://10.5.5.9/gp/gpControl/command/shutter?p=0
    '''

    if on_off == 'on':
        url = url + '/gp/gpControl/command/shutter?p=1'
    else:
        url = url + '/gp/gpControl/command/shutter?p=0'

    print ('url-----',url)

    try:
        response = requests.get(url, timeout=10)  # タイムアウトを10秒に設定
        if 200 <= response.status_code < 300:
            print("Request was successful.")
            # 応答内容を表示
            print(response.text)
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

'''
dirを指定して、そのdirのmp4をすべて取得する

'''

def copy_to_take_name(dir,takename):

    dir = dir.replace('\\','/')

    #一階層上のフォルダ名を取得
    sep = dir.split('/')

    newpath = '/'.join(sep[:-1]) + '/' + takename + '/'

    #フォルダがなければ作成
    if not os.path.exists(newpath):
        os.makedirs(newpath)

    #dirを指定して、そのdirのmp4をすべて取得する

    print ('copy_to_take_name : dir',dir)

    mp4s = glob.glob(dir + '/*.mp4', recursive=True)

    print ('newpath',newpath,'mp4s',mp4s)

    copydict = {}

    kz = 1

    for o in sorted(mp4s):

        o = o.replace('\\','/')

        #stringで二桁にする
        kzstr = str(kz).zfill(2)

        copyname = newpath + 'cam' + kzstr + '_' + takename + '.mp4'

        copydict[o] = copyname

        #file copy
        print ('-------copy',kz,o,copyname)
        shutil.copy2(o,copyname)

        kz = kz + 1

    return newpath

def write_list_to_file(string_list, filename):


    """
    指定されたリストの各要素を改行区切りでファイルに書き出す。

    Parameters:
    string_list (list): 文字列のリスト。
    filename (str): 書き出すファイルの名前。
    """
    with open(filename, 'w', encoding='utf-8') as file:
        for item in string_list:
            file.write(f"{item}\n")



'''
def get(work=0):

    url = "http://172.20.195.51:8080/gp/gpMediaList"

    if work == 1:
        url = testurl
    elif work == 2:
        url = 'https://www.google.co.jp/'

    e = check_url(url)

    print ('------',e)
'''

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

#demoui()
def make_timeurl(url,timedict):

    urlbase = url + '/gopro/camera/set_date_time?'
    
    #date=2022131&time=345&tzone=-120&dst=1
    
    k = 'date'
    urlbase = urlbase + k + '=' + str(timedict[k]) + '&'
    
    k = 'time'
    urlbase = urlbase + k + '=' + str(timedict[k]) + '&'
    
    k = 'tzone'
    urlbase = urlbase + k + '=' + str(timedict[k]) + '&'    
    
    k = 'dst'
    urlbase = urlbase + k + '=' + str(timedict[k])
    
    return urlbase

def get_time():

    #now
    # 現在の日時を取得（日本時間）、zoneinfoを使用
    now_zoneinfo = datetime.now(ZoneInfo('Asia/Tokyo'))

    # 辞書に格納するフォーマットを更新
    date_str_zoneinfo = now_zoneinfo.strftime('%Y_%m_%d')
    time_str_zoneinfo = now_zoneinfo.strftime('%H_%M_%S')
    tzone_minutes_zoneinfo = now_zoneinfo.utcoffset().total_seconds() // 60

    # 辞書を作成
    now = {
        'date': date_str_zoneinfo,
        'time': time_str_zoneinfo,
        'tzone': int(tzone_minutes_zoneinfo),
        'dst': 0  # 固定
    }

    print ('now',now)



    geturls = []
    seturls = []

    print ('-------time')
    for o in gopro_dict.keys():
        #print ('-------time',o)

        seturls.append(make_timeurl(o,now))
        #make_timeurl(o,now)
    #時計を合わせる
    ret_json_data_palla(seturls)   


    for o in gopro_dict.keys():
        #print ('-------time',o)

        geturls.append(o+'/gopro/camera/get_date_time')

    # 処理の開始時間を記録
    start_time = time.time()
    results = ret_json_data_palla(geturls)    

    #keyをsort
    results = dict(sorted(results.items()))        

    # 処理の終了時間を記録
    end_time = time.time()

    # 経過時間を計算（秒単位）
    elapsed_time = end_time - start_time

    # 経過時間をプリント
    print(f"時計を合わせる: {elapsed_time}秒")

    for o in results.keys():
        print ('-------',o,results[o])

def format_mac_address(mac):
    """
    Format a MAC address to the standard colon-separated format.

    Args:
        mac: the MAC address as a string of 12 hexadecimal digits.

    Returns:
        The MAC address formatted with colons.
    """
    if len(mac) != 12:
        raise ValueError("MAC address should be 12 hexadecimal digits")
    return ':'.join(mac[i:i+2] for i in range(0, len(mac), 2))

def wol_all():

    for o in gopro_dict.keys():

        print ('-------',o)

        #print (gopro_dict[o])

        #{'url': 'http://172.25.113.51:8080', 'name': 'HERO12 Black04', 'checkurl': 'http://172.25.113.51:8080/gp/gpMediaList', 'ap_mac_addr': '06574710694f'}

        ip_address = gopro_dict[o]['url'].split(':')[1].split('/')[-1]
        mac_address = format_mac_address(gopro_dict[o]['ap_mac_addr'])

        
        port = 9

        print (ip_address)
        print (mac_address)
        print (port)

        print (len(mac_address),'<<<')

        send_magic_packet(mac_address, ip_address, port=port)

        print ('try to send WOL :',gopro_dict[o]['name'])

        # 1秒間のポーズ
        time.sleep(1)