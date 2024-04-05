import os
import sys

# 現在のファイルのディレクトリ絶対パスを取得
current_dir = os.path.dirname(os.path.abspath(__file__))

# Pythonの検索パスにこのディレクトリを追加
if current_dir not in sys.path:
    sys.path.append(current_dir)