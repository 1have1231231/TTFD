from flask import Flask, send_file, Response
import os

app = Flask(__name__)

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/styles.css')
def styles():
    return send_file('styles.css', mimetype='text/css')

@app.route('/script.js')
def script():
    return send_file('script.js', mimetype='application/javascript')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
