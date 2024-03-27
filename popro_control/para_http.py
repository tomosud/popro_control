import asyncio
import aiohttp
import time
import os

async def download_one(url, save_path):
    start = time.time()
    chunk_size = 4096
    filename = url.split('/')[-1]

    print ('------url',url)
    print ('save_path',save_path)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=600) as resp:
                # レスポンスステータスコードが200以外の場合にエラーをログに記録
                if resp.status != 200:
                    print(f"Error {resp.status} while fetching {url}")
                    return
                
                print(f"Start: {resp.status}: {url}")
                
                with open(save_path, 'wb') as fd:
                    while True:
                        chunk = await resp.content.read(chunk_size)
                        #print ('chunk')
                        if not chunk:
                            break
                        fd.write(chunk)

        except Exception as e:
            # 例外が発生した場合のエラーログ
            print(f"An error occurred: {e}, while downloading {url}")
            return

    elapsed = round(time.time() - start)
    print(f"End: {filename}: {elapsed}s")

def download_many(url_dict, appnd_savepath):
    loop = asyncio.get_event_loop()
    
    # コルーチンをタスクに変換
    to_do = [loop.create_task(download_one(k, appnd_savepath + '/' + v)) for k, v in url_dict.items()]

    wait_coro = asyncio.wait(to_do)
    res, _ = loop.run_until_complete(wait_coro)
    loop.close()
    return len(res)

def download_main(url_dict, appnd_savepath):
    start = time.time()
    count = download_many(url_dict, appnd_savepath)
    elapsed = time.time() - start
    msg = '\n{} files downloaded in {:.2f}s'

    print(msg.format(count, elapsed))

def download_make_dict_and_do(urls=[],folder_path='C:/temp/DL'):

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    url_dict = {}

    for o in urls:
        
        file_name = o.split('/')[-1]
        #save_path = os.path.join(folder_path,file_name).replace('\\','/')
        save_path = file_name.replace('\\','/')

        print ('save_path',save_path)

        url_dict[o] = save_path

    download_main(url_dict, folder_path)

# 使用例
# url_dict = {'http://example.com/file1.zip': 'file1.zip', ...}
# appnd_savepath = '/path/to/save/directory/'
# download_main_do(url_dict, appnd_savepath)
