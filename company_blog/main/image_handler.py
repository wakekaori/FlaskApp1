# 画像ファイルを扱うための関数を記述(view関数から呼び出し)
# ブログ投稿ページで選択されたアイキャッチ画像指定のフォルダに格納しファイル名を返す関数
# view関数ではここで返すファイル名を受け取り後から画像ファイルを取り出せるようDBへ登録する(DBへの登録はview関数で実行)

import os   # ファイルやディレクトリを扱うために使用する
from PIL import Image   # 画像処理ライブラリ
from flask import current_app   # 現在実行中のアプリの情報が格納


def add_featured_image(upload_image):       # upload_image=ファイルオブジェクトを受け取る
    image_filename = upload_image.filename  # ファイルオブジェクトからファイル名を取得して変数へ格納
    # join=引数で渡したpathやファイル名を繋げてフルパスを作成(current_app.root_path=company_blogフォルダまでが格納)
    filepath = os.path.join(current_app.root_path, 'static/featuring_image', image_filename)    # 画像ファイルの保存先のパスを指定
    # filepath = os.path.join(current_app.root_path, r'static\featuring_image', image_filename)  # 画像ファイルの保存先のパスを指定(Windows)
    # windowsの場合pathは\で区切られるが、そのまま\を記述するとエスケープシーケンス(改行的なもの)となるため[r(=raw文字列)]を使用する
    image_size = (800, 800)             # 表示する画像サイズを設定
    image = Image.open(upload_image)    # 受け取った画像ファイルを開く
    image.thumbnail(image_size)         # 画像ファイルをサムネイルに変換
    image.save(filepath)                # 指定したバスに画像ファイルを保存
    return image_filename               # 保存したファイルを後から取り出せるようにファイル名を返す