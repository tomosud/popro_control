
'''
一時的なテスト用のファイルです。
'''
import command as cm
import ui as ui
import para_http

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

#r = cm.ret_gopros()
#print ('exsist',len(r.keys()),r)

ui.main()

'''
urls =['https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_20mb.mp4',
'https://sample-videos.com/video321/mp4/480/big_buck_bunny_480p_20mb.mp4',
'https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_20mb.mp4']

para_http.download_make_dict_and_do(urls=urls)
'''
print ('done')

