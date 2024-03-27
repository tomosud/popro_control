#非同期で行いたいhttp処理の集約

import asyncio
import aiohttp
import time
import os

async def download_one(url,save_path):
    start = time.time() #1
    chunk_size = 10 #2
    extention = 'zip'
    filename = url.split('/')[-1]

    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=600) as resp: #3
            print('start: {}: {}'.format(resp.status,url))

            #save_path = './{}.{}'.format(filename, extention)
            
            with open(save_path, 'wb') as fd:
                while True:
                    chunk = await resp.content.read(chunk_size) #4
                    if not chunk:
                        break
                    fd.write(chunk)

    elapsed = round(time.time() - start)
    print('end: {}: {}s'.format(filename, elapsed))

def download_many(url_list):
    loop = asyncio.get_event_loop() #5
    to_do = [download_one(url) for url in url_list] #6
    wait_coro = asyncio.wait(to_do) #7
    res, _ = loop.run_until_complete(wait_coro) #8
    loop.close()
    return len(res) #9


#{url:save_filename}とappnd savepathを設定する

def download_main_do(url_dict,appnd_savepath):

    
    start = time.time() #10
    count = download_many(url_dict)
    elapsed = time.time() - start
    msg = '\n{} files downloaded in {:.2f}s'

    print(msg.format(count, elapsed))


    


