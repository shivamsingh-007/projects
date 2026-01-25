from flask import Flask, jsonify
import random
from datetime import datetime

app = Flask(__name__)

@app.route('/api/scan', methods=['POST'])
def scan():
    print("🎯 SCAN ENDPOINT HIT!")
    return jsonify({
        'success': True,
        'result': {
            'alert_level': 0,
            'alert_name': 'NORMAL',
            'confidence': 0.95,
            'networks_found': 5,
            'threats_detected': 0,
            'timestamp': datetime.now().isoformat(),
            'ip_address': '127.0.0.1',
            'networks': []
        }
    })

@app.route('/test.html')
def test():
    return '''
    <button onclick="scan()">TEST SCAN</button>
    <script>
    async function scan() {
        const res = await fetch('/api/scan', {method: 'POST'});
        const data = await res.json();
        alert(JSON.stringify(data, null, 2));
    }
    </script>
    '''

if __name__ == '__main__':
    print("\n🧪 Test Server")
    print("Open: http://localhost:5000/test.html")
    print("Click button to test /api/scan\n")
    app.run(debug=True, port=5000)