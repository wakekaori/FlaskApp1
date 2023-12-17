# Webアプリの初期処理に関するコードを管理
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝DB関連＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
from flask_login import LoginManager

app = Flask(__name__)   # Flaskクラスのインスタンスを作成して変数appへ代入(これによりアプリケーションオブジェクトが作成されFlaskの機能を利用できるようになる)

app.config['SECRET_KEY'] = 'mysecretkey'    # アプリの環境変数[SECRET_KEY]に対して秘密鍵を設定する(フォームを使用する場合は必須の項目)
                                            # アプリの環境変数は←のように辞書形式で設定することができる
                                            # 右辺の文字列はランダムな文字列でOK
                                            # アプリ単位で異なる秘密鍵を設定し、秘密鍵の内容は公開厳禁(flask_wtfでセキュリティ(CSRF)対策に使用するため)
                                            # 本来は秘密鍵をコーディングせず、環境変数として設定する
# flask_wtfでセキュリティ(CSRF)対策を行うために必要
# トークンを利用して正しいリクエストを識別する
# 【トークンの実装方法】
# 1.ブラウザからリクエストがあったら
# 2.Webアプリ側でトークン(ランダムな文字列)を生成し保存する(トークンの生成に使われるのが秘密鍵になる)
# 3.生成したトークンをHTMLにhiddenで埋め込みブラウザに送信する
# 4.ブラウザで入力した情報とトークンを合わせてWebアプリに送信する
# 5.リクエストを受け取るWebアプリ側では2で保存したトークンと送信されたトークンが一致するか確認する
# トークンが一致すれば通常の処理を行い、一致しなければ不正なリクエストとして扱う
# ブラウザの更新するたびにトークンは変更される
# ↑とHTMLのFormタグ内に「{{ form.hidden_tag() }}」を記述することで実装できる

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝DB関連＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# 環境変数の設定
basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
uri = os.environ.get('DATABASE_URL')    # デプロイするPaaSで環境変数が何になるか調べて[DATABASE_URL]を変更する(herokuの場合:DATABASE_URL)
if uri: # デプロイした場合の処理
    if uri.startswith('postgres://'):   # 変数uriが[postgres://]で始まっているか確認 ※デプロイするサーバによって適宜変更
        uri = uri.replace('postgres://', 'postgresql://', 1)    # デプロイするサーバによって適宜変更 ※[1]は文字列の先頭から1つ目を置換
        app.config['SQLALCHEMY_DATABASE_URI'] = uri # 環境変数[SQLALCHEMY_DATABASE_URI]へ格納
else:   # ローカルの場合の処理(ローカルの場合、変数uriは空白になるから)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://morge:19820501@localhost'  # postgresql://ユーザー名:password@localhost
    ### postgresqlインストールするとdefaultでpostgresが設定されている(PWはroot？？)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DBの作成とMigrateの準備
db = SQLAlchemy(app)
Migrate(app, db)
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# ログインマネージャーの設定
login_manager = LoginManager()  # LoginManagerをインスタンス化して使用できるようにする
login_manager.init_app(app)     # LoginManagerにappを渡す(アプリとログイン機能を紐づける)
login_manager.login_view = 'users.login' # 未ログインユーザーがログイン後のページにアクセスしようとすると転送されるview関数(login)を指定
# view関数[login]=ログインページを表示するview関数(Blueprint名.view関数名を指定する)

# 未ログインユーザーがログイン必須画面にアクセスしてログインページへredirectした際に表示する、ログイン要求メッセージを日本語にする処理
def localize_callback(*args, **kwargs):
    return 'このページにログインするにはアクセスが必要です'

login_manager.localize_callback = localize_callback     # def localize_callbackを呼び出して

# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝DB関連＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝
# 外部キー制約の有効化(SQLite専用)
# from sqlalchemy.engine import Engine
# from sqlalchemy import event

# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()
# ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝

# 実装したBlueprintをFlaskのアプリケーションへ登録(view関数関連のファイルのBlueprint名をインポート)
from company_blog.main.views import main
from company_blog.users.views import users
from company_blog.error_pages.handlers import error_pages

# 各viewsファイルでBlueprintを有効化
app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(error_pages)
