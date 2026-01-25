from flask import Flask, send_file
import os

app = Flask(__name__)

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

print(f"\nProject Root: {PROJECT_ROOT}\n")

@app.route('/')
def home():
    return send_file(os.path.join(PROJECT_ROOT, 'frontend', 'test.html'))

@app.route('/test.html')
def test():
    return send_file(os.path.join(PROJECT_ROOT, 'frontend', 'test.html'))

@app.route('/static/css/<filename>')
def css(filename):
    path = os.path.join(PROJECT_ROOT, 'static', 'css', filename)
    print(f"CSS Request: {path}")
    print(f"Exists: {os.path.exists(path)}")
    return send_file(path, mimetype='text/css')

@app.route('/static/js/<filename>')
def js(filename):
    path = os.path.join(PROJECT_ROOT, 'static', 'js', filename)
    print(f"JS Request: {path}")
    print(f"Exists: {os.path.exists(path)}")
    return send_file(path, mimetype='application/javascript')

if __name__ == '__main__':
    print("Starting test server...")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)