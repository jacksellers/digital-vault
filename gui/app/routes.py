from flask import render_template
from app import app


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/trade')
def trade():
    return render_template('trade.html')
