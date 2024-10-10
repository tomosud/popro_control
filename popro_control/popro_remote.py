import asyncio
from pynput import keyboard

# 音量アップ時の処理
async def volume_up():
    print("Start Recording")

# 音量ダウン時の処理
async def volume_down():
    print("Stop Recording")

# キーが押されたときの処理
def on_press(key):
    if key == keyboard.Key.media_volume_up:
        asyncio.run_coroutine_threadsafe(volume_up(), loop)  # 非同期で音量アップを実行
    elif key == keyboard.Key.media_volume_down:
        asyncio.run_coroutine_threadsafe(volume_down(), loop)  # 非同期で音量ダウンを実行
        pass

# キーリスナーを開始する関数
def start_key_listener():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# 非同期で実行されるタスク
async def some_async_task():
    while True:
        #print("Doing something else asynchronously...")
        await asyncio.sleep(2)

# メインの非同期関数
async def main():
    # キーリスナーを非同期で実行
    listener_task = asyncio.to_thread(start_key_listener)

    # 他の非同期タスクを並行して実行
    await asyncio.gather(listener_task, some_async_task())

# 非同期イベントループを開始
def start_remote():
    print ('start remote!!')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())