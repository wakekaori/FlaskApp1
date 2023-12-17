# 主要機能のview関数を管理(Blueprintを実装)

from flask import Blueprint, flash, render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from company_blog.models import BlogCategory, BlogPost, Inquiry
from company_blog.main.forms import BlogCategoryForm, UpdateCategoryForm, BlogPostForm, BlogSearchForm, InquiryForm
from company_blog.main.image_handler import add_featured_image
from company_blog import app, db 

main = Blueprint('main', __name__)

@main.route('/category_maintenance', methods=['GET','POST'])
@login_required
def category_maintenance():
    with app.app_context():
        page = request.args.get('page', 1, type=int)
        blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).paginate(page=page, per_page=10)
        form = BlogCategoryForm()

        if form.validate_on_submit():
            blog_category = BlogCategory(category=form.category.data)
            db.session.add(blog_category)
            db.session.commit()
            flash('ブログカテゴリが追加されました')
            return redirect(url_for('main.category_maintenance'))
        elif form.errors:
            form.category.data = ""
            flash(form.errors['category'][0])   
            # フィールド:categoryに設定されたエラーメッセージを表示(forms.pyで設定したdef validate_categoryのメッセージを表示)

    return render_template('category_maintenance.html', blog_categories=blog_categories, form=form)
    
@main.route('/<int:blog_category_id>/blog_category', methods=['GET','POST'])
@login_required
def blog_category(blog_category_id):
    if not current_user.is_administrator():
        abort(403)
    with app.app_context():
        blog_category = BlogCategory.query.get_or_404(blog_category_id)
        form = UpdateCategoryForm(blog_category_id)
        if form.validate_on_submit():
            blog_category.category = form.category.data
            db.session.commit()
            flash('カテゴリが更新されました')
            return redirect(url_for('main.category_maintenance'))
        elif request.method == 'GET':
            form.category.data = blog_category.category
    return render_template('blog_category.html', form=form)

@main.route('/<int:blog_category_id>/delete_category', methods=['GET', 'POST'])
@login_required
def delete_category(blog_category_id):
    if not current_user.is_administrator():
        abort(403)
    with app.app_context():
        blog_category = BlogCategory.query.get_or_404(blog_category_id)
        db.session.delete(blog_category)
        db.session.commit()
    flash('カテゴリが削除されました')
    return redirect(url_for('main.category_maintenance'))

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    with app.app_context():
        form = BlogPostForm()
        if form.validate_on_submit():
            if form.picture.data:   # アイキャッチ画像が選択されているか確認
                pic = add_featured_image(form.picture.data) # image_handler.pyのdefを実行することでファイルを保存し変数[pic]へファイル名を格納
            else:
                pic = ''    # アイキャッチ画像が選択されていなければ変数には空文字を格納
            blog_post = BlogPost(title=form.title.data, text=form.text.data, featured_image=pic, user_id=current_user.id, category_id=form.category.data, summary=form.summary.data)  # フォームに入力されたデータをBlogPostモデルへ入れる
            db.session.add(blog_post)
            db.session.commit()
            flash('ブログが投稿されました')
            return redirect(url_for('main.blog_maintenance'))
    return render_template('create_post.html', form=form)

@main.route('/blog_maintenance')
@login_required
def blog_maintenance():
    page = request.args.get('Page', 1, type=int)
    blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # DBからブログ記事を取得(ID降順)
    return render_template('blog_maintenance.html', blog_posts=blog_posts)

@main.route('/<int:blog_post_id>/blog_post')
def blog_post(blog_post_id):
    form = BlogSearchForm()
    blog_post = BlogPost.query.get_or_404(blog_post_id) # blog_post_idでDB検索し変数へ格納
    recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()    # カテゴリの取得
    return render_template('blog_post.html', post=blog_post, recent_blog_posts=recent_blog_posts, blog_categories=blog_categories, form=form)    # 格納した変数をblog_postテンプレートへ渡す

@main.route('/<int:blog_post_id>/delete_post', methods=['GET', 'POST'])
@login_required
def delete_post(blog_post_id):
    with app.app_context():
        blog_post = BlogPost.query.get_or_404(blog_post_id)
        if blog_post.author != current_user:
            abort(403)  # 対象の記事の投稿者以外の場合は処理を中止する
        db.session.delete(blog_post)
        db.session.commit()
    flash('ブログ投稿が削除されました')
    return redirect(url_for('main.blog_maintenance'))

@main.route('/<int:blog_post_id>/update_post', methods=['GET', 'POST'])
@login_required
def update_post(blog_post_id):
    with app.app_context():
        blog_post = BlogPost.query.get_or_404(blog_post_id)
        if blog_post.author != current_user:
            abort(403)
        form = BlogPostForm()
        if form.validate_on_submit():
            blog_post.title = form.title.data
            if form.picture.data:
                blog_post.featured_image = add_featured_image(form.picture.data)    # アイキャッチ画像が更新された場合のみDB更新
            blog_post.text = form.text.data
            blog_post.summary = form.summary.data
            blog_post.category_id = form.category.data
            db.session.commit()
            flash('ブログ投稿が更新されました')
            return redirect(url_for('main.blog_post', blog_post_id=blog_post.id))
        elif request.method == 'GET':
            form.title.data = blog_post.title
            form.picture.data = blog_post.featured_image
            form.text.data = blog_post.text
            form.summary.data = blog_post.summary
            form.category.data = blog_post.category_id 
            print(blog_post.featured_image)
            
    return render_template('create_post.html', form=form)

@main.route('/')
def index():
    form = BlogSearchForm()
    page = request.args.get('Page', 1, type=int)
    blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # ブログ記事の取得
    recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()    # カテゴリの取得

    return render_template('index.html', blog_posts=blog_posts, recent_blog_posts=recent_blog_posts, blog_categories=blog_categories, form=form)

@main.route('/search', methods=['GET', 'POST'])
def search():
    form = BlogSearchForm()
    search_text = ""    # formに入力された検索文字列を格納する変数を初期化
    if form.validate_on_submit():
        search_text = form.search_text.data # search_textへ検索フォームに入力した文字列を格納
    elif request.method == 'GET':
        form.search_text.data = ""  # GETリクエストの場合は検索フォームの内容をクリアする

    # 入力された検索条件を元にブログ記事を絞り込む
    page = request.args.get('Page', 1, type=int)
    blog_posts = BlogPost.query.filter((BlogPost.text.contains(search_text)) | (BlogPost.title.contains(search_text)) | (BlogPost.summary.contains(search_text))).order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # 条件で絞ったブログ記事の取得
    # 本文が条件の文字列と一致したデータに絞る=filter(BlogPost.text.contains(search_text))
    # 複数の条件で絞る=filter((BlogPost.text.contains(search_text)) | (BlogPost.title.contains(search_text))) ※条件ごとに()で囲んで半角スペースと|で羅列する
    recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()    # カテゴリの取得

    return render_template('index.html', blog_posts=blog_posts, recent_blog_posts=recent_blog_posts, blog_categories=blog_categories, form=form, search_text=search_text)

@main.route('/<int:blog_category_id>/category_posts')
def category_posts(blog_category_id):
    form = BlogSearchForm()
    blog_category = BlogCategory.query.filter_by(id=blog_category_id).first_or_404()  # ヘッダー表示用カテゴリ名の取得(取得できない場合は404)
    page = request.args.get('Page', 1, type=int)
    blog_posts = BlogPost.query.filter_by(category_id=blog_category_id).order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # カテゴリIDで絞って記事を取得
    # blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).paginate(page=page, per_page=10)   # ブログ記事の取得
    recent_blog_posts = BlogPost.query.order_by(BlogPost.id.desc()).limit(5).all()  # 最新記事の取得
    blog_categories = BlogCategory.query.order_by(BlogCategory.id.asc()).all()    # カテゴリの取得

    return render_template('index.html', blog_posts=blog_posts, recent_blog_posts=recent_blog_posts, blog_categories=blog_categories, blog_category=blog_category, form=form)
    # blog_categories=サイドバーのカテゴリ一覧/blog_category=ヘッダー表示用カテゴリ名

@main.route('/inquiry', methods=['GET', 'POST'])
def inquiry():
    form = InquiryForm()
    if form.validate_on_submit():
        with app.app_context():
            inquiry = Inquiry(name=form.name.data, email=form.email.data, title=form.title.data, text=form.text.data)
            db.session.add(inquiry)
            db.session.commit()
        flash('お問い合わせが送信されました')
        return redirect(url_for('main.inquiry'))
    return render_template('inquiry.html', form=form)

@main.route('/inquiry_maintenance')
@login_required
def inquiry_maintenance():
    page = request.args.get('page', 1, type=int)
    inquiries = Inquiry.query.order_by(Inquiry.id.desc()).paginate(page=page, per_page=10)
    return render_template('inquiry_maintenance.html', inquiries=inquiries)

@main.route('/<int:inquiry_id>/display_inquiry')
@login_required
def display_inquiry(inquiry_id):
    inquiry = Inquiry.query.get_or_404(inquiry_id)  # get_or_404=PrimaryKeyでの検索が必須
    # inquiry = Inquiry.query.filter_by(id=inquiry_id).first_or_404()   # get_or_404と同じ結果になる
    form = InquiryForm()
    form.name.data = inquiry.name
    form.email.data = inquiry.email
    form.title.data = inquiry.title
    form.text.data = inquiry.text
    print(inquiry)
    return render_template('inquiry.html', form=form, inquiry_id=inquiry_id)

@main.route('/<int:inquiry_id>/delete_inquiry', methods=['GET', 'POST'])
@login_required
def delete_inquiry(inquiry_id):
    if not current_user.is_administrator():
        abort(403)
    with app.app_context():
        inquiry = Inquiry.query.get_or_404(inquiry_id)
        db.session.delete(inquiry)
        db.session.commit()
    flash('お問い合わせが削除されました')
    return redirect(url_for('main.inquiry_maintenance'))

@main.route('/info')
def info():
    return render_template('info.html')