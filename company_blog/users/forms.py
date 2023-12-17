# ユーザーに関するformのコードを管理
from flask_wtf import FlaskForm # flask_wtfからFlaskFormクラスをインポート
from wtforms import ValidationError, StringField, PasswordField, SubmitField # wtformsからStringField, PasswordField, SubmitField各クラス(使用するフィールドだけ)をインポート
# ValidationErrorをimportすることでモデルに設定したunique(=重複不可)の列で同じ内容を登録しようとしたときにエラーメッセージを表示
from wtforms.validators import DataRequired, Email, EqualTo # wtforms > validatorsの使用する内容だけインポート
# DataRequired=必須入力チェック/ Email=メールアドレス形式のチェック/ EqualTo=2つのフィールドが同じかチェック
# WTForms Validatorsによる入力チェックの種類：Python+Flask動画>セクション9>78.Formの入力チェック>1:25頃を参照
# 入力チェックの設定はformのクラスで行う
# これで設定した入力チェックはview関数の[def register]内の「validate_on_submit」で実行、チェックされる

# Flask-Loginの機能=1.ログイン,ログアウトを行う/2.ログイン状態(ログイン済or未ログイン)を管理する/3.ログインが必要なページを保護する
# 【ログインページの実装】
# ログインマネージャーの設定 ※ユーザーのログイン状態(ログイン済or未ログイン)を管理する機能
# Userモデルの変更
# ログイン用フォームの追加、テンプレートの編集
# ログイン用view関数の追加
# ログインユーザー名の表示(navバー)

from company_blog.models import User


class LoginFrom(FlaskForm): # FlaskFormを継承してログイン用クラスを作成する
    email = StringField('email',validators=[DataRequired(),Email(message='メールアドレスが不正です')])
    password = PasswordField('password',validators=[DataRequired()])
    submit = SubmitField('ログイン')

class RegistrationForm(FlaskForm):  # FlaskFormを継承してユーザー登録するクラスを作成する
    # クラス内にFormに表示する各フィールドを定義して、HTMLへ各フィールドを配置しブラウザで表示する
    # WTFormsの主なフィールドの種類：Python+Flask動画>セクション9>72.Formの基本1>5:15頃を参照
    email = StringField('メールアドレス',validators=[DataRequired(), Email(message='メールアドレスが不正です')])   # StringField=テキスト入力欄('フィールド名')    ※ここで指定したフィールド名をブラウザに表示することができる
    # validatorsで入力チェックを行う内容を指定する(ここでは入力必須項目とメールアドレス形式のチェックをしている)
    # validatorsのパラメータ：messageへエラーメッセージを設定し、テンプレートのフィールドごとにメッセージを表示する領域を定義すると各入力フィールドの直下に指定したメッセージが表示される
    # テンプレートのフィールドごとにメッセージを表示する領域自体は共通化できるためhelperファイル(=jinja2のマクロ)を作成して定義する
    # マクロ=引数を受け取って処理を行い値を返すことができる(今回はマクロでフィールドを受け取ってフィールドを表示し、エラーメッセージがあればフィールドの下に表示する)
    # helperファイルはマクロファイルと分かるようにファイル名の先頭に"_"をつける
    username = StringField('ユーザー名',validators=[DataRequired()])
    password = PasswordField('パスワード',validators=[DataRequired(),EqualTo('pass_confirm', message='パスワードが一致していません')])  # PasswordField=パスワード入力欄('フィールド名')
    # 入力チェックの[EqualTo]は引数に文字列で対象となる変数名を記述する。また、一方だけに定義する
    pass_confirm = PasswordField('パスワード(確認)',validators=[DataRequired()])    # [password]でEqualToを設定しているためこちらでは定義不要
    submit = SubmitField('登録')    # SubmitField=送信ボタン('Value')

    def validate_username(self, field):
        # フォームに入力されたユーザー名がすでにテーブルに存在すればエラーにする
        # [validate_]で始まりフィールド名(=username)のメソッドを定義することで、[def register]の「if form.validate_on_submit()」が実行されたときに「def validate_username」も実行され、フォームのフィールド(=今回はユーザー名)のチェックを行うことができるようになる
        # 引数の[field]はフォームのフィールド(=今回はusernameのfield)を受け取っている
        if User.query.filter_by(username=field.data).first():
            # filter_by(条件)=今回の場合、username列がフォームのユーザー名フィールドのデータと一致するもの ※filter_by(テーブル列名=フォームのフィールドの内容)
            # =フォームに入力されたユーザー名でusersテーブルを検索してfirstで最初の1件のデータを取得
            # データが取得されたらTrueになる
            raise ValidationError('入力されたユーザー名はすでに使われています')
            # raise=自作関数で例外を発生させるときに使用する
            # wtformsのインポートしたクラス[ValidationError]の引数にメッセージを定義する

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスはすでに使われています')

class UpdateUserForm(FlaskForm):    # FlaskFormを継承してユーザー情報を更新するクラスを作成する
    email = StringField('メールアドレス', validators=[DataRequired(), Email()]) # message='メールアドレスが不正です'
    username = StringField('ユーザー名',validators=[DataRequired()])
    password = PasswordField('新パスワード',validators=[EqualTo('pass_confirm',message='パスワードが一致していません')])
    pass_confirm = PasswordField('新パスワード(確認)')
    submit = SubmitField('更新')

    def __init__(self, user_id, *args, **kwargs):    # ユーザー情報に対して何かしら処理する場合はuseridが必要になるため、formにuseridを格納しておくと便利
        super(UpdateUserForm, self).__init__(*args, **kwargs)   # このまま記述すると継承元(FlaskForm)のinit(初期化処理)が上書きされるため次の記述を行う
        self.id = user_id   # 初期値として受け取ったuser_idを属性に設定する(このidを元に対象のユーザーの情報を処理する)

    def validate_email(self, field):
        # 更新対象のuser以外「filter(User.id != self.id)」でフォームに入力されているアドレスと同じメールアドレスを持つレコードがないか確認
        if User.query.filter(User.id != self.id).filter_by(email=field.data).first():
            raise ValidationError('入力されたメールアドレスはすでに使われています')
        
    def validate_username(self, field):
        if User.query.filter(User.id != self.id).filter_by(username=field.data).first():
            raise ValidationError('入力されたユーザー名はすでに使われています')