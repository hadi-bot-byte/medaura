from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import hashlib
import time
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# ========== CONFIGURATION ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
FILES_DB = os.path.join(BASE_DIR, 'files.json')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Storage nodes configuration
NODES = [
    {'id': 'node1', 'ip': '192.168.1.101', 'status': 'online', 'storage_used': 42, 'storage_total': 500, 'cpu': 4, 'ram': 16},
    {'id': 'node2', 'ip': '192.168.1.102', 'status': 'online', 'storage_used': 35, 'storage_total': 500, 'cpu': 4, 'ram': 16},
    {'id': 'node3', 'ip': '192.168.1.103', 'status': 'online', 'storage_used': 48, 'storage_total': 500, 'cpu': 4, 'ram': 16},
    {'id': 'node4', 'ip': '192.168.1.104', 'status': 'online', 'storage_used': 28, 'storage_total': 500, 'cpu': 4, 'ram': 16},
    {'id': 'node5', 'ip': '192.168.1.105', 'status': 'online', 'storage_used': 52, 'storage_total': 500, 'cpu': 4, 'ram': 16},
]

# ========== HELPER FUNCTIONS ==========
def load_files():
    """Load files from JSON database"""
    try:
        if os.path.exists(FILES_DB) and os.path.getsize(FILES_DB) > 0:
            with open(FILES_DB, 'r', encoding='utf-8') as f:
                files = json.load(f)
                return files if isinstance(files, list) else []
    except:
        pass
    return []

def save_files(files):
    """Save files to JSON database"""
    try:
        with open(FILES_DB, 'w', encoding='utf-8') as f:
            json.dump(files, f, indent=2, ensure_ascii=False)
    except:
        pass

def format_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes is None or size_bytes == 0:
        return "0 B"
    
    size = float(size_bytes)
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    for unit in units:
        if size < 1024.0 or unit == 'TB':
            return f"{size:.1f} {unit}"
        size /= 1024.0
    
    return f"{size:.1f} TB"

# ========== FRONTEND ROUTES ==========
@app.route('/')
def index():
    """Serve the main cloud drive page"""
    try:
        return send_file('cloud-drive.html')
    except:
        return "Cloud Drive API is running! Upload cloud-drive.html to this folder."

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('.', filename)
    except:
        return jsonify({'error': 'File not found'}), 404

# ========== API ROUTES ==========
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    files = load_files()
    return jsonify({
        'status': 'healthy',
        'server': 'Cloud Drive API',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'files_count': len(files),
        'nodes_count': len(NODES)
    })

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get all storage nodes"""
    return jsonify(NODES)

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get all uploaded files"""
    files = load_files()
    return jsonify(files)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Generate unique ID
        file_id = hashlib.md5(f"{file.filename}_{time.time()}".encode()).hexdigest()[:12]
        
        # Save file
        save_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{file.filename}")
        file.save(save_path)
        
        # Create metadata
        file_meta = {
            'id': file_id,
            'name': file.filename,
            'size': file_size,
            'size_formatted': format_size(file_size),
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'path': save_path
        }
        
        # Save to database
        files = load_files()
        files.append(file_meta)
        save_files(files)
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file': file_meta
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a file by ID"""
    files = load_files()
    for file in files:
        if file.get('id') == file_id:
            file_path = file.get('path')
            if file_path and os.path.exists(file_path):
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=file.get('name', 'download')
                )
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file by ID"""
    try:
        files = load_files()
        
        # Find the file
        for i, file in enumerate(files):
            if file.get('id') == file_id:
                # Delete physical file
                file_path = file.get('path')
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                
                # Remove from database
                files.pop(i)
                save_files(files)
                
                return jsonify({'success': True, 'message': 'File deleted successfully'})
        
        return jsonify({'error': 'File not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== START APPLICATION ==========
if __name__ == '__main__':
    print("=" * 60)
    print("CLOUD DRIVE API - COMPLETE VERSION")
    print("=" * 60)
    print(f"Server URL: http://localhost:5001")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Database: {FILES_DB}")
    print(f"Storage nodes: {len(NODES)}")
    print("=" * 60)
    
    app.run(debug=True, port=5001, host='127.0.0.1')