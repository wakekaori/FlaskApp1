# エラーページに関するview関数を管理(view関数関連のためBlueprintの実装が必要)
from flask import render_template, Blueprint

error_pages = Blueprint('error_pages', __name__)    # Blueprintをインスタンス化する 
# ['error_pages']=Blueprint名 以降は'error_pages'で参照できるようになる/[__name__]=このviews.pyのディレクトリが格納されている

# 権限がない場合に表示するエラーページのルーティング(権限制御で使用)※sourceはflask_basicへ格納
# すべての[@app]→[@Blueprint名]に変更
# @error_pages.errorhandler(403)  # 独自のエラーページを返す関数を作成(403はアクセス禁止(=権限無し)のエラーステータス)
@error_pages.app_errorhandler(403)  # errorhandlerは1つのBlueprintの範囲内だけで有効な関数のため、アプリケーション全体で有効な関数にするには[errorhandler→app_errorhandler]に変更する 
def error_403(error):   # 引数でエラーの情報を渡す
    return render_template('error_pages/403.html'), 403

@error_pages.app_errorhandler(404)  # 独自のエラーページを返す関数を作成(404は存在しないページのエラーステータス)
def error_404(error):   # 引数でエラーの情報を渡す
    return render_template('error_pages/404.html'), 404 # エラーページのテンプレートを指定(対照のファイルが別のフォルダにある場合は相対パスを記述)
                                                        # ファイル名の後に「, エラーに対応するステータスコード」を記述してレスポンスとして返す