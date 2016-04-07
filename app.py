# app.py
from flask import Flask, request, render_template

app = Flask(__name__, static_url_path='/static')

@app.route('/hello')
def hello():
	return 'Hello world!'

@app.route('/')
def root():
	return render_template('home.html')

@app.route('/profile', methods=['POST'])
def search():
	print(request.form['search'])
	return render_template('profile.html', search=request.form['search'])

@app.route('/redirect', methods=['GET', 'POST'])
def redirect():
	return render_template('home.html')


if __name__ == '__main__':
	app.run()
