from setuptools import setup, find_packages

setup(
    name='popro_control',
    version='0.12',
    packages=find_packages(),
    install_requires=[
        'requests',  # 依存関係としてrequestsを追加
        'dearpygui==1.11.1',  # dearpyguiのバージョンを1.11.1に指定
        'tzdata',  # tzdataを追加 タイムゾーンの設定に使用
        'aiohttp',  # aiohttpを追加
        'aiofiles',  # aiofilesを追加
        'psutil',  # psutilを追加
    ]
)
