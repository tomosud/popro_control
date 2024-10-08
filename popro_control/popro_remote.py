import requests
import json

remote_token = None

def ret_url(key="recordValue"):
    global remote_token

    if remote_token is None:
        json_path = "C:/GoPro/Rename_Setting.ini"
        
        with open(json_path, 'r') as f:
            data = json.load(f)

        if 'api_remote' not in data:
            print('Please fill in the blanks in Rename_Setting.ini')
            return None

        remote_token = data['api_remote']

    url = f"https://ezdata.m5stack.com/api/store/{remote_token}/{key}"
    print(f'URL: {url}')  # URLの出力を修正

    return url

def write_value(value):
    url = ret_url()  # ret_url関数を呼び出す
    if url is None:
        return None

    headers = {'Content-Type': 'application/json'}
    data = {'value': value}
    response = requests.post(url, json=data, headers=headers)
    return response.json()

def read_value():
    url = ret_url()  # ret_url関数を呼び出す
    if url is None:
        return None
    
    response = requests.get(url)
    return response.json()

# 使用例
result = read_value()
print(result)
