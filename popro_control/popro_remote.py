import asyncio
import popro_ui  # UI関数が定義されているモジュール
from pynput import keyboard

# グローバル変数としてイベントループを宣言
loop = None

# 音量アップ時の処理
async def volume_up():
    print("Start Recording")
    userdata = ['startRecording', 0]
    popro_ui.send_server_command_do(user_data)


# 音量ダウン時の処理
async def volume_down():
    print("Stop Recording")
    userdata = ['stopRecording', 0]
    popro_ui.send_server_command_do(user_data)

# キーが押されたときの処理
def on_press(key):
    global loop  # グローバル変数としてイベントループを使う
    if key == keyboard.Key.media_volume_up:
        asyncio.run_coroutine_threadsafe(volume_up(), loop)  # 非同期で音量アップを実行
    elif key == keyboard.Key.media_volume_down:
        asyncio.run_coroutine_threadsafe(volume_down(), loop)  # 非同期で音量ダウンを実行

# キーリスナーを非同期で実行する関数
async def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        while True:
            await asyncio.sleep(0.1)  # 非同期のリスナーを定期的にチェック

# 非同期で実行されるタスク
async def some_async_task():
    while True:
        await asyncio.sleep(2)  # 他の非同期タスク

# メインの非同期関数
async def main():
    # UIを非同期で実行（UIがブロッキングしないようにスレッドで実行）
    ui_task = asyncio.to_thread(popro_ui.main)

    # キーリスナーを非同期で実行
    listener_task = asyncio.create_task(start_key_listener())

    # 他の非同期タスクと並行して実行
    await asyncio.gather(ui_task, listener_task, some_async_task())

# 非同期イベントループを開始
def start_remote():
    global loop  # グローバル変数としてイベントループを設定
    print('start remote!!')
    
    # 新しいイベントループを作成して設定
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(main())

start_remote()
