# ユーザーに関するview関数を管理(view関数関連のためBlueprintの実装が必要)

# FlaskでFormを作成する場合、wtforms(ライブラリ)とflask_wtf(flaskの拡張機能)をインストール&インポートして使用する
# wtforms=Formの作成に使用するPythonのライブラリ。
# flask_wtf=wtformsのflask専用のもの
from flask import render_template, url_for, redirect, session, flash, request, abort
# flask内のFlaskクラスをインポート, テンプレートをインポート
# Webアプリでメッセージを表示する場合に[flash]機能を使用する↑
# ページネーションをflaskで使用するときに[request]機能を使用する↑
# abort=権限制御(処理を途中で中止する際)に使用する↑


# LoginManager=ユーザーのログイン状態(ログイン済or未ログイン)を管理する機能
# UserMixin=クラス作成時の各メソッドや属性の継承用
# login_user=ログイン機能
from flask_login import login_user ,logout_user, login_required, current_user
# check_password_hash=ハッシュ化されたパスワードと一致しているか確認/generate_password_hash=登録するパスワードをハッシュ化
# login_required=未ログインユーザーからページの保護をする機能/current_user=ログインユーザーの情報を格納(権限制御で使用)

from company_blog import app
from company_blog import db
from company_blog.models import User, BlogPost, BlogCategory
from company_blog.users.forms import RegistrationForm, LoginFrom, UpdateUserForm
from company_blog.main.forms import BlogSearchForm
from flask import Blueprint

users = Blueprint('users', __name__)    # Blueprintをインスタンス化する 
# ['users']=Blueprint名 以降は'users'で参照できるようになる/[__name__]=このviews.pyのディレクトリが格納されている

@users.route('/login',methods=['GET', 'POST'])  # すべての[@app]→[@Blueprint名]に変更
def login():
    form = LoginFrom()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:    # 該当するemailが存在する場合の処理
            if user.check_password(form.password.data): # Userモデルのcheck_passwordメソッドでフォームに入力されたPWとDBのPWを比較
                # 一致していた場合の処理
                login_user(user)    # 引数にユーザー情報を渡せばログイン状態にできる機能
                next = request.args.get('next') # ログイン必須ページからログインページに自動転送されてきた場合のクエリ文字列(=URL)を変数へ格納
                if next == None or not next[0] == '/':  # クエリ文字列にURLが設定されていないorクエリ文字列の1文字目が相対URLで[/]以外の場合
                    next = url_for('main.blog_maintenance')  # ログイン必須ページからログインページに自動転送されてきた場合管理ページを変数へ格納
                    # views.pyに記述する場合は('Blueprint名.view関数名')とする※view関数を呼び出すときはBlueprint名を付ける必要がある
                return redirect(next)   # 変数に格納したURLを表示
            else:
                # 一致していない場合の処理
                flash('パスワードが一致しません')    
        else:
            # 該当するemailが存在しない場合の処理
            flash('emailの登録がありません')

    return render_template('users/login.html', form=form) # loginフォームを表示(インスタンス化したフォームを渡す) ※templates>users内のファイルを参照するため[users/]を追加

@users.route('/logout')   # メソッドを実行してredirectするだけなのでmethodsはGETのみとなる(=省略)
@login_required
def logout():
    logout_user()   # インポートしたlogout_userを実行することでログアウトする
    return redirect(url_for('users.login'))   # loginページを表示する


@users.route('/register',methods=['GET','POST'])  # view関数でフォームを処理するためメソッドを定義する(GET=データの表示/POST=データの登録)
# GETとPOSTそれぞれのメソッドのリクエストを受け取れるように両方定義する(何も指定しないとGETだけが指定されている状態になる)
# ブラウザからwebサーバーに送られてくるリクエストの種類：Python+Flask動画>セクション9>73.Formの基本2>0:55頃を参照
@login_required
def register():
    form = RegistrationForm()       # フォームをインスタンス化してFormの機能を使用できるようにする(↑のクラス)
    # 管理者のみユーザー登録できるようにする(権限制御)
    if not current_user.is_administrator():
        abort(403)  # registerページを表示(=view関数:registerが呼ばれた)場合、管理者ユーザー以外なら処理を中止して403エラーを表示
    
    if form.validate_on_submit():   # フォームが送信され、かつ入力された内容に問題がないか確認
                                    # ↑のクラスの各フィールドに入力チェックを定義するとvalidate_on_submitが実行されたときにエラーチェックが行われる
                                    # ※行われるエラーチェックはRegistrationFormクラスの「def validate_~」に記述
                                    # 入力チェックで問題がなければ各項目に入力されたデータをDB(またはセッション)に保持する
                                    # セッション=データを一時的に保持する領域
                                    # ※ユーザーがサイトにアクセスした時点でセッションが始まり、最初のページから次のページへと通信が続いている間、一時的に情報を管理する
        # sessionに書き込む
        # session['email'] = form.email.data
        # session['username'] = form.username.data
        # session['password'] = form.password.data

        # DBへ書き込む
        with app.app_context():
            user = User(email=form.email.data, username=form.username.data, password=form.password.data, administrator="0")
            db.session.add(user)
            db.session.commit()

        flash('ユーザーが登録されました')   # インポートしたflash機能を使用してメッセージを表示する(user_maintenanceページに表示される)
        return redirect(url_for('users.user_maintenance'))    # formの必要な情報を書き込んだらユーザー管理ページへ処理を転送する
    return render_template('users/register.html', form=form)  # URL[/register]を呼び出した場合と入力内容が誤っている場合はユーザ登録ページを表示
# 【まとめ】/registerにリクエストが送られたときの流れ
# 1.フォームを作成  form = RegistrationForm()
# 2.ユーザー登録ページを表示    return render_template('register.html', form=form)
#   ※まだ表示しただけでformに入力されていないためif文は処理されず最後のrender_templateが実行される
# 3.formの登録ボタンが押されると再度view関数が呼ばれ(=render_templateで'registeer.html'が指定されており再度registeer.htmlにリクエストが送られるから)、Formに入力済みのためif文が実行される

@users.route('/user_maintenance') # ユーザー管理ページは表示するだけのためmethodsの定義は不要(GETのみリクエストを受け取ればOKのため省略)
@login_required
# ↑未ログインユーザーから保護したいページのview関数にこのデコレーターを記述することで上部に記述した、login_manager.login_view = 'login'
# (=ログインマネージャーに対して設定されたview関数[login])が実行される=loginページが表示される
def user_maintenance():
    # usersテーブルの情報をユーザー管理ページへ表示
    # users = User.query.order_by(User.id).all()  # idを昇順で全件取得し変数へ格納
    # 昇順=order_by(クラス名.列名) / 降順=order_by(クラス名.列名.desc())

    # ページネーションの実装方法=app.pyでrequestをインポート&下記を記述→テンプレートへ記述
    page = request.args.get('page', 1, type=int)    # requestのクエリ文字列から現在のページを取得し変数へ格納
    # クエリ文字列=URLの末尾(URLの「?」以降)についている文字列のこと ※「/user_maintenance?page=現在のページ」になる予定
    # クエリ文字列で現在のページを格納するコード=テンプレートへ記述 / 格納された現在のページの値を取得=app.pyのview関数(request.args.get('page', 1, type=int)の部分)
    # 'page':クエリ文字列のページの値を取得 / 1:現在のページを取得できなかった場合のデフォルトのページ(=1ページ目) / type=int:取得した値をintに変換
    users = User.query.order_by(User.id).paginate(page=page, per_page=10) # flaskのrequest機能を使いページネーションを実装することができるようになる
    # usersはページネーションオブジェクトとなる。ページネーションオブジェクトには様々な属性がありそれらを元にデータを表示することができる(テンプレートへ記述)
    # ページネーションオブジェクトの属性の種類:Python+Flask動画>セクション10>103.ページネーション2>0:45頃を参照
    # per_page=1ページ当たりの件数(指定しなければ20件表示)
    return render_template('users/user_maintenance.html', users=users)    # ユーザー管理ページへ変数を渡す

@users.route('/<int:user_id>/account', methods=['GET', 'POST'])
# int型でuser_idを受け取り対象レコードの更新フォームを表示(=GET)、更新ボタンクリックによりフォームの内容でDBを更新(=POST)、ユーザー管理ページへ遷移
@login_required
def account(user_id):
    with app.app_context():
        user = User.query.get_or_404(user_id)   # get_or_404=user_idで検索できればDBのレコードを変数へ格納、できなければ404エラーを格納
        # 更新対象がログインユーザーではなくand管理者ではない場合は処理を中止して403エラーを表示
        if user.id != current_user.id and not current_user.is_administrator():
            abort(403)

        form = UpdateUserForm(user_id)  # ユーザーidをフォームに格納
        if form.validate_on_submit():   # 更新ボタンクリック時の処理(=フォームが送信され、かつ入力された内容に問題がないか確認)
            # DBへの更新処理
            user.username = form.username.data  # フォームに入力されたユーザー名をモデルに格納
            user.email = form.email.data        # フォームに入力されたメールアドレスをモデルに格納
            if form.password.data:  # フォームにパスワードが入力されているか確認(パスワード入力時のみ処理するため)
                user.password = form.password.data  # フォームに入力されたパスワードをsetterを通じてプロパティ：passwordに設定する
            db.session.commit()
            flash('ユーザーアカウントが更新されました')
            return redirect(url_for('users.user_maintenance'))    # ユーザー管理ページへ遷移
        elif request.method == 'GET':   # 初期表示の処理を記述(対象レコードの更新フォームを表示)
            # User.query.get_or_404(user_id)で取得した対象ユーザーの情報を更新フォームに格納(各右辺の[user]はメソッドの最初の変数名を示す)
            form.username.data = user.username  # フォームのユーザー名フィールドにDBから取得したユーザー名を格納
            form.email.data = user.email        # フォームのメールアドレスフィールドにDBから取得したメールアドレスを格納
    return render_template('users/account.html', form=form)   # form = UpdateUserForm(user_id)で作成したフォームをHTMLに渡す
    # 更新ボタンをクリックすると再度account.htmlが呼び出されるが、その時はPOSTリクエストになる

# 削除ボタンクリック時に呼び出されるview関数
@users.route('/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    with app.app_context():
        user = User.query.get_or_404(user_id)
        # 管理者以外は処理を中止して403エラーを表示(=アカウント削除できないようにする)
        if not current_user.is_administrator():
            abort(403)
        # 管理者アカウントは削除できないようにする
        if user.is_administrator():
            flash('管理者は削除できません')
            return redirect(url_for('users.account', user_id=user_id))
        
        db.session.delete(user)
        db.session.commit()
    flash('ユーザーアカウントが削除されました')
    return redirect(url_for('users.user_maintenance'))

@users.route('/<int:user_id>/user_posts')
@login_required
def user_posts(user_id):
    form = BlogSearchForm()
    user = User.query.filter_by(id=user_id).first_or_404()    # 表示用ユーザー名の取得
    page = request.args.get('Page', 1, type=int)
    blog_posts = BlogPost.query.filter_by(user_id=user_id).order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # ユーザーで絞り込んだデータを取得
    # blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # ブログ記事の取得
    recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()    # カテゴリの取得

    return render_template('index.html', blog_posts=blog_posts, recent_blog_posts=recent_blog_posts, blog_categories=blog_categories, user=user, form=form)