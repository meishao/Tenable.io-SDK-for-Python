#!/bin/env/python
# coding: utf-8
from flask import Flask, request, render_template
from datetime import datetime
from tenable_io.api.models import Folder
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
import json

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

@app.route('/scans_template/')
# 診断テンプレートのリスト取得
def scans_template():
    client = TenableIOClient()
    tpl = client.editor_api.list('scan')
    return render_template('index.html', data=tpl.templates)

if __name__ == "__main__":
    #import os
    port = 8000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run(host='0.0.0.0', port=port)
