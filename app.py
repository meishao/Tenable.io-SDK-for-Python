#!/bin/env/python
# coding: utf-8
from flask import Flask, request, render_template, Response
from datetime import datetime
from time import time
from functools import wraps
import os

from tenable_io.api.models import Folder
from tenable_io.api.models import Scan
from tenable_io.api.scans import ScansApi, ScanCreateRequest, ScanExportRequest, ScanImportRequest, ScanLaunchRequest

from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
import json

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'admin'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

app = Flask(__name__)

@app.route('/')
def index():
    # 「templates/index.html」のテンプレートを使う
    # 「message」という変数に"Hello"と代入した状態で、テンプレート内で使う
    return render_template('index.html', message="Hello")

@app.route('/folder')
@app.route('/folder/<int:folderid>')
# フォルダ情報取得
# 取得情報をオブジェクト形式出力
def getFolder():
    client = TenableIOClient()
    _folders = client.folders_api.list().folders
    return render_template('index.html', data=_folders)

@app.route('/getFolders')
# フォルダ情報取得
# 取得情報をJSON形式出力
def getFolders():
    client = TenableIOClient()
    resp = client.get('folders')
    return render_template('index.html', message=resp.text)

@app.route('/scans_template')
@requires_auth
# 診断テンプレートのリスト取得
def scans_template():

    # インスタンス初期化
    client = TenableIOClient()
    tpl = client.editor_api.list('scan')
    return render_template('index.html', data=tpl.templates)

@app.route('/host_reg/<string:hostname>/<string:template>')
@requires_auth
# 診断対象を登録する
# 登録に必要なパラメータ
# name: 診断対象名　（例：google）
# text_targets: 診断対象のホスト名或はIPアドレス　（例：www.google.com）
# templete: 診断テンプレート　（例：basic | 診断テンプレート一覧　/scan_templateを参照）
def host_reg(hostname, template):
    
    if len(hostname) != 0:
        # インスタンス初期化
        client = TenableIOClient()
        # 新規診断対象を登録する
        scan = client.scan_helper.create(
            name=hostname, 
            text_targets=hostname,
            template=template
        )
        # assert scan.name() = scan_name
        msg = str(scan.id) + "|" + scan.name() + u"が正常に登録できました。"
        return render_template('index.html', message=msg)
    else:
        return render_template('index.html', message=u"HOST_REG|不正アクセスを記録しました。")

#@app.route('/scans/ope')
@app.route('/scans/<string:ope>/<int:id>')
@requires_auth
# 診断対象を操作する
# 実行に必要なパラメータ
# ope: launch, pause, stop, delete, resume
# id: 診断対象ID 
def scan_ope(ope, id):
    
    if ope == 'status':
        # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        # 診断IDより診断対象取得
        scan_b = client.scan_helper.id(id)
        return render_template('index.html', message=str(scan_b.status()))    
    elif ope == 'launch':
        # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        # 診断IDより診断対象取得
        scan_b = client.scan_helper.id(id)
        scan_b.launch(id)
        return render_template('index.html', message=str(scan_b.status()))
    elif ope == 'pause':
        # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        client.scans_api.pause(id)
        # 診断IDより診断対象取得
        scan_b = client.scan_helper.id(id)
        return render_template('index.html', message=str(scan_b.status()))
    elif ope == 'stop':
         # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        client.scans_api.stop(id)
        # 診断IDより診断対象取得
        scan_b = client.scan_helper.id(id)
        return render_template('index.html', message=str(scan_b.status()))
    elif ope == 'resume':
        # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        client.scans_api.resume(id)
        # 診断IDより診断対象取得
        scan_b = client.scan_helper.id(id)
        return render_template('index.html', message=str(scan_b.status()))
    elif ope == 'delete':
        # インスタンス初期化
        client = TenableIOClient()    
        # 診断対象のID或は登録名が入力画面もしくは入力パラメータから渡される
        resp = client.scans_api.delete(id)
        # 削除結果を確認する
        if resp is True:
            return render_template('index.html', message=u"診断対象を正しく削除できました。")
        else:
            return render_template('index.html', message=u"診断対象を削除できませんでした。")
    else:
        return render_template('index.html', message=u"SCAN_OPE|不正アクセスを記録しました。")

@app.route('/report/request/<int:scan_id>')
@requires_auth
# 診断レポートRAWデータを要求する
# RAWデータ：　脆弱性診断データ（CSV）、ホスト情報
# scan_id: 診断対象登録時、発行するID
# 応答：　レポートファイル(file ID)が返す
def report_request(scan_id):
    
    if scan_id:
        # インスタンス初期化
        client = TenableIOClient()
        # レポートRAWデータをCSV形式で出力する要求をする
        request_uri = 'scans/' + str(scan_id) + '/export'
        resp = client.post(request_uri, ScanExportRequest(format=u'csv'), path_params={'scan_id':scan_id})
        if resp.status_code == 200:
            obj_msg = json.loads(resp.text)
            str_msg = str(obj_msg.get('file')) + u'|レポート要求が正常に受信できました。'
            return render_template('index.html', message=str_msg)
        else:
            return render_template('index.html', message=u"REPORT_REQUEST_ERROR|レポート要求時エラーが発生しています。")
    else:
        return render_template('index.html', message=u"REPORT_REQUEST|不正アクセスを記録しました。")

@app.route('/report/<string:ope>/<int:scan_id>/<int:file_id>')
@requires_auth
# 要求レポートの生成状況確認及びダウンロード
# 実行に必要なパラメータ
# ope: status, download
# scan_id: 診断対象ID
# file_id: レポートファイルID
def report_ope(ope, scan_id, file_id):
    # インスタンス初期化
    client = TenableIOClient()
    # 一時レポートCSVファイル名
    todaynow = datetime.today().strftime('%Y%m%d%H%M%S')
    tenable_csv_folder = '/app/csv_report/tenable/'
    tenable_csv_file = tenable_csv_folder + str(todaynow) + '_scanid_' + str(scan_id) + '.csv'
    if os.path.isdir(tenable_csv_folder):
        pass
    else:
        os.makedirs(tenable_csv_folder)
    if ope == 'status':
        request_uri = 'scans/' + str(scan_id) + '/export/' + str(file_id) + '/status'
        resp = client.get(request_uri, path_params={'scan_id':scan_id, 'file_id':file_id})
        obj_msg = json.loads(resp.text)
        str_msg = obj_msg.get('status')
        return render_template('index.html', message=str_msg)
    elif ope == 'download':
        request_uri = 'scans/' + str(scan_id) + '/export/' + str(file_id) + '/download'
        resp = client.get(request_uri, path_params={'scan_id':scan_id, 'file_id':file_id}, stream=True)
        iter_content = resp.iter_content(chunk_size=1024)
        with open(tenable_csv_file, mode='wb') as fd:
            for ck in iter_content:
                fd.write(ck)
        str_msg = u'https://tenable-io.herokuapp.com/' + tenable_csv_file 
        return render_template('index.html', message=str_msg)
    else:
        return render_template('index.html', message=u"REPORT_OPE|不正アクセスを記録しました。")
    
if __name__ == "__main__":
    #import os
    port = 8000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run(host='0.0.0.0', port=port)
