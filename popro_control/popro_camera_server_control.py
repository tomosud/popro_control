import requests
import json
import time

# 使用例
server_url = ""
test_server_url = r"http://10.102.106.60:810"

# カメラリスト
all_cameras = []

## カメラリスト debugにも使うのでall_camerasと分けた
status_cameras = []
'''
以下を操作するための関数
https://www.toolsforgopro.com/cameratools_server

'''
# JSONデータを読みやすく整形して出力する関数
def print_pretty_json(data):
    try:
        # 整形して出力
        formatted_json = json.dumps(data, indent=4, ensure_ascii=False)
        print(formatted_json)
    except (TypeError, ValueError) as e:
        print(f"Error: {str(e)}")

#カメラのリストをdictで返す
def get_all_cameras():
    try:
        # URLの設定
        #url = f"{server_url}/camera/command"

        #url = server_url
        
        # リクエストデータ
        payload = {
            "command": "getAllCameras"
        }
        
        # POSTリクエストを送信
        response = requests.post(server_url, json=payload)
        
        # レスポンスの確認
        if response.status_code == 200:
            return response.json()  # カメラリストをJSON形式で取得
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"


#camera_command 機能の実行部分　sendCameraCommandで、カメラにコマンドを送信する後述のコマンドが使える
#sendCameraCommand = False で、cameraCommandではなく通常のCommandを送信する
def send_camera_command_do(camera_list,camera_command,sendCameraCommand=True):

    '''
    {

    connectToCamera: Connects to the camera(s) via Bluetooth.
    disconnectFromCamera: Disconnects from the camera(s).
    sleepCamera: Sends the camera(s) into sleeping state.
    startRecording: Starts recording.
    stopRecording: Stops recording.
    tagMoment: Tags the moment.
    enableWiFi: Enables the camera(s)' WiFi (without connecting to the WiFi!).
    disableWiFi: Disables the camera(s)' WiFi.
    startLivePreviewMode: Starts the live preview mode on one camera (this requires an active WiFi connection to the camera!). The live preview video can then be streamed with ffmpeg or other tools.
    stopLivePreviewMode: Stops the live preview mode on one camera (this requires an active WiFi connection to the camera!).

        "command": "sendCameraCommand",
        "cameras": ["GP123456"],
        "cameraCommand": "startRecording"
    }
    '''

    try:
        # URLの設定
        #url = f"{server_url}/camera/command"

        #url = server_url
        #通常のCommandは以下のような構造
        payload = {
                "command": camera_command,
                "cameras": camera_list,
            }
        if sendCameraCommand:
        #sendCameraCommand以下のような構造
        # リクエストデータ
            payload = {
                "command": "sendCameraCommand",
                "cameras": camera_list,
                "cameraCommand": camera_command
            }
        
        # POSTリクエストを送信
        response = requests.post(server_url, json=payload)
        
        # レスポンスの確認
        if response.status_code == 200:
            return response.json()  # JSON形式で取得
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"



def set_server_url(url):
    
    global server_url

    server_url = url

    print("Server URL is set to ",server_url)



def connect_all_cameras(try_to_connect = True):

    global all_cameras
    
    '''
    {
        "command": "sendCameraCommand",
        "cameras": ["GP123456"],
        "cameraCommand": "startRecording"
    }
    {'cameras': [{'connection_state': 'connected', 'name': 'HERO12 Black01 (172.24.106.51)'}, {'connection_state': 'connected', 'name': 'HERO12 Black02 (172.26.186.51)'}, {'connection_state': 'connected', 'name': 'HERO12 Black03 (172.20.195.51)'}, {'connection_state': 'connected', 'name': 'HERO12 Black04 (172.25.113.51)'}, {'connection_state': 'connected', 'name': 'HERO12 Black05 (172.22.164.51)'}], 'command': 'getAllCameras', 'status_code': 0}
    '''
    nc_camera_list = []

    camera_dict = get_all_cameras()

    print (camera_dict)

    if camera_dict["status_code"] == 0:
        # カメラリストの取得に成功

        for on in camera_dict['cameras']:
            if on['connection_state'] == 'connected':
                all_cameras.append(on['name'])
            else:
                #print(on['name'])
                # 接続してないカメラをリストに追加
                nc_camera_list.append(on['name'])

    if len (nc_camera_list) == 0:
        print("All cameras are connected.")
        return True
    
    else:   
    
        for on in nc_camera_list:
            print(on,' is not connected.')
            # カメラに接続
            #connect_camera(on)
        if try_to_connect:
            send_camera_command_do(nc_camera_list,'connectToCamera')

        else:
            return False

    #一秒待つ

    time.sleep(0.5)

    test = connect_all_cameras(try_to_connect = False)

    if test:
        print("---All cameras are connected now.")

        return True


def send_camera_command(camera_command):

    if connect_all_cameras():

        send_camera_command_do(all_cameras,camera_command)

    else:
        print("Error: same Cameras are not connected. or some error occured.")
        return False
    

#####
#testにも使うのでserver_urlを引数に追加
def get_staus_all_cameras(server_url_now=''):
    
    global status_cameras
    status_cameras = []

    if len(status_cameras) == 0:

        if server_url_now == '':
            #setされてる前提
            server_url_now = server_url
        else:
            set_server_url(server_url_now)

        cameras_dict = get_all_cameras()

        for o in cameras_dict['cameras']:
            status_cameras.append(o['name'])

        print (len(status_cameras),status_cameras)

    '''
    {
	"command": "cameraStatus",
	"cameras": ["GP123456"]
    }
    '''
    cameraStatus_dict = send_camera_command_do(status_cameras,'cameraStatus',sendCameraCommand=False)
    
    #print(cameraStatus_dict)
    print_pretty_json(cameraStatus_dict)

    return cameraStatus_dict

def dbug():
    print("dbug")
    get_staus_all_cameras(server_url_now=test_server_url)

#send_camera_command('startRecording')

if __name__ == "__main__":
    dbug()
    #demoui()