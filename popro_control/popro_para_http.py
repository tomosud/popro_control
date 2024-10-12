import asyncio
import aiohttp
import aiofiles
import time
import os
#from aiofiles import open as aio_open
import popro_ui

async def download_one(session, url, save_path):
    start = time.time()
    print(f"------url: {url}")
    print(f"save_path: {save_path}")

    async with session.get(url, timeout=600) as resp:
        # レスポンスステータスコードが200以外の場合にエラーをログに記録
        if resp.status != 200:
            print(f"Error {resp.status} while fetching {url}")
            return
        
        print(f"Start: {resp.status}: {url}")

        popro_ui.gopro_button_color_update(url,work='copying')
        
        async with aiofiles.open(save_path, 'wb') as fd:
            while True:
                chunk = await resp.content.read(4096000)
                if not chunk:
                    break
                await fd.write(chunk)
                
    elapsed = round(time.time() - start)
    filename = url.split('/')[-1]
    print(f"End: {filename}: {elapsed}s")
    popro_ui.gopro_button_color_update(url,work='base')

async def download_many(url_dict, appnd_savepath):
    async with aiohttp.ClientSession() as session:
        tasks = [download_one(session, k, appnd_savepath + '/' + v) for k, v in url_dict.items()]
        await asyncio.gather(*tasks)
        return len(tasks)

async def download_main(url_dict, appnd_savepath):
    start = time.time()
    count = await download_many(url_dict, appnd_savepath)
    elapsed = time.time() - start
    msg = f'\n{count} files downloaded in {elapsed:.2f}s'
    print(msg)

#ふつうはこれを使う
def download_main_wrapper(url_dict, appnd_savepath):
    asyncio.run(download_main(url_dict, appnd_savepath))

def download_make_dict_and_do(urls=[], folder_path='C:/temp/DL'):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    url_dict = {}
    for o in urls:
        file_name = o.split('/')[-1]
        save_path = file_name.replace('\\', '/')
        url_dict[o] = save_path
    
    asyncio.run(download_main(url_dict, folder_path))



