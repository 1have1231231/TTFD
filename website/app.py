from flask import Flask, send_file, Response
import os

app = Flask(__name__)

# Get the directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return send_file(os.path.join(BASE_DIR, 'index.html'))

@app.route('/styles.css')
def styles():
    return send_file(os.path.join(BASE_DIR, 'styles.css'), mimetype='text/css')

@app.route('/script.js')
def script():
    return send_file(os.path.join(BASE_DIR, 'script.js'), mimetype='application/javascript')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
