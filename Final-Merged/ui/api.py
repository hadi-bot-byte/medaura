from flask import Flask, jsonify 
app = Flask(__name__) 
app = Flask(__name__) 
 
@app.route('/api/health') 
def health(): 
    return jsonify({'status': 'healthy'}) 
 
@app.route('/api/nodes') 
def nodes(): 
    return jsonify([ 
        {'id': 'node1', 'ip': '192.168.1.101'}, 
        {'id': 'node2', 'ip': '192.168.1.102'}, 
        {'id': 'node3', 'ip': '192.168.1.103'}, 
        {'id': 'node4', 'ip': '192.168.1.104'}, 
        {'id': 'node5', 'ip': '192.168.1.105'} 
    ]) 
 
if __name__ == '__main__': 
    app.run(port=5001) 
