from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, TextAreaField, SelectField
# TextAreaField=複数行のフィールド/SelectField=プルダウンのフィールド
from wtforms.validators import DataRequired, Email
from company_blog.models import BlogCategory
from flask_wtf.file import FileField, FileAllowed   # ファイルを扱うフィールドの定義に使用(画像のアップロードに使用する)

class BlogCategoryForm(FlaskForm):
    category = StringField('カテゴリ名', validators=[DataRequired()])
    submit = SubmitField('保存')

    def validate_category(self, field):
        if BlogCategory.query.filter_by(category=field.data).first():
            raise ValidationError('すでに登録されています')
        
class UpdateCategoryForm(FlaskForm):
    category = StringField('カテゴリ名', validators=[DataRequired()])
    submit = SubmitField('更新')

    def __init__(self, blog_category_id, *args, **kwargs):   # 削除対象のカテゴリidを渡す
        super(UpdateCategoryForm, self).__init__(*args, **kwargs)   # FlaskForm(継承元)のinit処理を継承するため記述(=ここのinitで完全に上書きさせないための処理)
        self.id = blog_category_id

    def validate_category(self, field):
        if BlogCategory.query.filter_by(category=field.data).first():
            raise ValidationError('すでに登録されています')
        
class BlogPostForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired()])
    category = SelectField('カテゴリ', coerce=int)
    # coerce=保持するデータの型(選択肢は文字になるけど内部的にはカテゴリIDとなるためintを指定)
    summary = StringField('要約', validators=[DataRequired()])
    text = TextAreaField('本文', validators=[DataRequired()])   # 複数行の場合はTextAreaFieldを定義
    picture = FileField('アイキャッチ画像', validators=[FileAllowed(['jpg','png'])])
    # FileAllowed=アップロードできるファイルの拡張子を指定できる
    submit = SubmitField('投稿')

    # カテゴリの選択肢として表示するカテゴリ名をDBから取得
    # メソッド名の先頭に[ _ ]を付けることでこのクラス内部用に定義できる ※このクラスの初期処理(def __init__)からしか呼び出せない
    def _set_category(self):
        blog_categories = BlogCategory.query.all()  # ブログカテゴリをDBからすべて取得
        # self.category=↑で定義した属性はSelectFieldのため選択肢が必要 ※choice=パラメータ
        # SelectFieldの選択肢はchoiceパラメータにリスト形式内にタプル形式で設定する ※[(内部的な値1,表示するラベル1),(内部的な値2,表示するラベル2),...]
        # リスト内包表記で設定するために↓の右辺のように内包でblog_categories(=DBデータ)から1つずつblog_categoryに格納し、その内容を「(id,category)」形式で格納
        # 右辺は[]で囲まれているためリストにタプルが格納される
        self.category.choices = [(blog_category.id, blog_category.category) for blog_category in blog_categories]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_category()    # ↑で定義した内部用メソッドを呼び出してself.categoryのSelectFieldに設定

# サイドバーに表示している検索バー(=検索フォーム)用のフォーム
class BlogSearchForm(FlaskForm):
    search_text = StringField('検索テキスト', validators=[DataRequired()])
    submit = SubmitField('検索')

class InquiryForm(FlaskForm):
    name = StringField('お名前(必須)', validators=[DataRequired()])
    email = StringField('メールアドレス(必須)', validators=[DataRequired(), Email(message='メールアドレスが不正です')])
    title = StringField('題名')
    text = TextAreaField('メッセージ本文(必須)', validators=[DataRequired()])
    submit = SubmitField('送信')

    