# モデルに関するコードをすべて管理するファイル
from datetime import datetime
from pytz import timezone
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin

from company_blog import app, db, login_manager     # 同じ階層の__init__.pyからインポート

# Flask_loginで現在のログインユーザーの情報を保持し、必要な時に参照できるようにする
@login_manager.user_loader  # ユーザー認証にかかわる関数を指定
def load_user(user_id):    # 引数にはユーザーを認証する際にユーザーを識別する情報を指定
    with app.app_context():
        return db.session.get(User, user_id)    # useridを元にUserからデータを読み込み、そのユーザーの情報を返す
        # return User.query.get(user_id)
        # userid_1 = User.query.get(1)
        # userid_1 = db.session.get(User, 1)  # SQLAlchemy2.0以降はこちら

# ユーザー認証に用いるUserクラスを定義
class User(db.Model, UserMixin):   # テーブル(model)を作成※modelクラスがデータベースのテーブルになる(db.Modelを継承して作成)
    # UserMixinクラスを継承。クラス内にはflask_loginで使用する予め定められた属性やメソッドを定義する必要があるが、継承することで記述不要になる
    __tablename__ = 'users' # テーブル名を指定(これを記述しない場合はクラス名のuserがテーブル名になる)
    # テーブル内の列を定義する(列はクラスの属性として定義する)
    # 型の種類：Python+Flask動画>セクション10>89.データベースの作成>1:30頃 / オプションの種類2:15頃を参照
    # 引数に型や列のオプションを指定する
    id = db.Column(db.Integer, primary_key=True)    # Primary_keyは自動で数字が振られる
    email = db.Column(db.String(64), unique=True, index=True)    # Stringは最大文字数を指定できる
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128)) # ハッシュ化=暗号化的なもの(暗号化は元に戻すことが可能だけどハッシュ化はできない)
    administrator = db.Column(db.String(1)) # ←追加した列
    post = db.relationship('BlogPost', backref='author', lazy='dynamic')    # モデル：BlogPostとのリレーションシップを設定【1対多の設定方法】
    # post = db.relationship('BlogPost', backref='author', uselist=False)     # モデル：BlogPostとのリレーションシップを設定【1対1の設定方法】
    # backref='author'という名称でBlogPostモデルからUserモデルの属性を参照することができる
    # 【例】BlogPostモデルの__repr__でUserモデルの情報をauthorを用いることで表示できるようになる(記述方法はBlogPostの__repr__を参照)
    # lazy='dynamic' → モデルのデータを読み込むタイミングと方法を指定している
    # BlogPostモデルからUserモデルへはusers.idで動的に絞り込んでデータを読み込むため'dynamic'を指定 ※1対多
    
    # 初期化の処理(上記で定義した変数を引数に入れるがidは自動で番号が振られるためここでは含まない)
    def __init__(self, email, username, password, administrator): # ハッシュ化前のPWを受取→プロパティ名[password]に値を設定→property.setterでPWをハッシュ化し属性値[password_hash]へ格納
        # 受け取った値を属性に設定
        self.email = email
        self.username = username
        # self.password_hash = password_hash
        self.password = password   # self.password(=プロパティ名)とすることでpropertyのsetterの引数[password]へ値を設定できる
        self.administrator = administrator  # 追加した列の属性

    def __repr__(self): # printなどで画面出力するときにreturnで定義した内容を表示する特殊メソッド
        return f"UserName: {self.username}" # [UserName]というタイトルでself.usernameを表示する

    def check_password(self, password): # 入力されたパスワードを[password]で渡す
        return check_password_hash(self.password_hash, password)    # DBに登録されているハッシュ化されたパスワードと入力されたパスワードを比較

    # Userクラスのインスタンスに保持するがPWなど重要なデータは漏洩や安易な参照、書き換えを防ぐためpropertyを使用する
    # property=クラスに設定できる。クラスのインスタンスに保持するデータで、値の参照(getter)や変更方法を制限(setter)することが可能
    # propertyでは[setter]を通じてのみ変更ができる=予期せぬ変更を防ぐことができる
    # [def __init__]で設定していた属性値を[self.password_hash]→[self.password(=self.プロパティ名)]とすることでpropertyのsetterの引数[password]へ値を設定できる
    # ↑によりモデルの初期化時にPWが設定された場合はproperty.setterを通じて、ハッシュ化された後に属性値[password_hash]に格納される

    # ■値の設定(setter)
    # @プロパティ名.setter
    # def プロパティ名(self, 設定値):
    #   self.変数 = 設定値

    # ■値の参照(getter)
    # @property     ←固定
    # def プロパティ名(self): 
    #   return self.変数

    # 値の設定：インスタンス名.property名 = 設定値 / 値の参照：インスタンス名.property名

    # 値の参照(getter)
    @property
    def password(self):
        # getterではハッシュ化したPWを返すようにしてハッシュ化前のPWを直接返さないようにする
        raise AttributeError('password is not a readable attribute')    # ハッシュ化前のPWを参照しようとすると←のエラーメッセージを表示
    
    # 値の設定(setter)
    @password.setter
    def password(self, password):
        # setterではハッシュ化したPWをDBへ登録する
        self.password_hash = generate_password_hash(password)   # ハッシュ化(DBへの登録は各view関数で実行)

    # 管理者or一般ユーザーを返すメソッド(権限制御で使用)
    def is_administrator(self):
        if self.administrator == "1":
            return 1
        else:
            return 0
        
    # ユーザー管理ページに表示する投稿数を表示するメソッド(user_maintenance.htmlから呼び出す)
    def count_posts(self, userid):
        return BlogPost.query.filter_by(user_id=userid).count()

class BlogPost(db.Model):
    __tablename__ = 'blog_post'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # ForeignKey=外部キー制約を設定　※('users=テーブル名.id=列名')を指定
    # sqliteでは外部キー制約が無効化されているため有効化する必要がある　※Python+Flask動画>セクション10>95.リレーションシップ設定3>1:05頃参照
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'))
    date = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Tokyo'))) # 日時をデフォルトで入力(datetimeとtimezoneはライブラリのインポートが必要)
    title = db.Column(db.String(140))
    text = db.Column(db.Text)   # db.Text=長文の文字列を格納
    summary = db.Column(db.String(140)) # 記事の要約を格納する列
    featured_image = db.Column(db.String(140))  # アイキャッチ画像(=記事の特徴を示す画像)ファイルへのディレクトリを保持する属性値を定義

    def __init__(self, title, text, featured_image, user_id, category_id, summary):
        self.title = title
        self.text = text
        self.featured_image = featured_image
        self.user_id = user_id
        self.category_id = category_id
        self.summary = summary

    def __repr__(self):
        return f"PostID: {self.id}, Title: {self.title}, Author: {self.author}  \n"
    
class BlogCategory(db.Model):
    __tablename__ = 'blog_category'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(140))
    posts = db.relationship('BlogPost', backref='blogcategory', lazy='dynamic')

    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return f"CategoryID: {self.id}, CategoryName: {self.category} \n"
    
    # カテゴリ管理ページで投稿数を表示(取得)するためのメソッド(category_maintenance.htmlから呼び出して使う)
    def count_posts(self, id):
        return BlogPost.query.filter_by(category_id=id).count()

class Inquiry(db.Model):
    __tablename__ = 'inquiry'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    title = db.Column(db.String(140))
    text = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Tokyo')))

    def __init__(self, name, email, title, text):
        self.name = name
        self.email = email
        self.title = title
        self.text = text

    def __repr__(self):
        return f"InquiryId: {self.id}, Name: {self.name}, Text: {self.text} \n"