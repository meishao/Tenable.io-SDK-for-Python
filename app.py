#!/bin/env/python
# coding: utf-8
from flask import Flask, request, render_template
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def index():
    # 「templates/index.html」のテンプレートを使う
    # 「message」という変数に"Hello"と代入した状態で、テンプレート内で使う
    return render_template('index.html', message="Hello")
#def homepage():
#    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")

#    return """
#    <h1>Hello heroku</h1>
#    <p>It is currently {time}.</p>

#    <img src="http://loremflickr.com/600/400">
#    """.format(time=the_time)

#if __name__ == '__main__':
#    app.run(debug=True, use_reloader=True)
    
if __name__ == "__main__":
    #import os
    port = 8000

    # Open a web browser pointing at the app.
    # os.system("open http://localhost:{0}".format(port))

    # Set up the development server on port 8000.
    app.debug = True
    app.run(host='0.0.0.0', port=port)
