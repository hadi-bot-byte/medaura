from flask import Flask, request, jsonify, send_file, send_from_directory, session
from flask_cors import CORS
import os
import json
import hashlib
import time
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'cloud-drive-secret-key-2025'  # Secret key for sessions
CORS(app, supports_credentials=True)

# ========== CONFIGURATION ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
FILES_DB = os.path.join(BASE_DIR, 'files.json')
USERS_DB = os.path.join(BASE_DIR, 'users.json')

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Default admin user (username: admin, password: admin123)
DEFAULT_USERS = [
    {
        'id': 'user_001',
        'username': 'admin',
        'password': hashlib.sha256('admin123'.encode()).hexdigest(),  # Hashed password
        'email': 'admin@clouddrive.com',
        'role': 'admin',
        'created_at': datetime.now().isoformat()
    },
    {
        'id': 'user_002',
        'username': 'user1',
        'password': hashlib.sha256('password123'.encode()).hexdigest(),
        'email': 'user1@clouddrive.com',
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
]

# Storage nodes configuration
NODES = [
    {'id': 'node1', 'ip': '192.168.1.101', 'status': 'online', 'storage_used': 42, 'storage_total': 500},
    {'id': 'node2', 'ip': '192.168.1.102', 'status': 'online', 'storage_used': 35, 'storage_total': 500},
    {'id': 'node3', 'ip': '192.168.1.103', 'status': 'online', 'storage_used': 48, 'storage_total': 500},
    {'id': 'node4', 'ip': '192.168.1.104', 'status': 'online', 'storage_used': 28, 'storage_total': 500},
    {'id': 'node5', 'ip': '192.168.1.105', 'status': 'online', 'storage_used': 52, 'storage_total': 500},
]

# ========== HELPER FUNCTIONS ==========
def load_users():
    """Load users from JSON database"""
    try:
        if os.path.exists(USERS_DB) and os.path.getsize(USERS_DB) > 0:
            with open(USERS_DB, 'r', encoding='utf-8') as f:
                users = json.load(f)
                return users if isinstance(users, list) else DEFAULT_USERS
    except:
        pass
    return DEFAULT_USERS

def save_users(users):
    """Save users to JSON database"""
    try:
        with open(USERS_DB, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to save users: {e}")

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
    except Exception as e:
        print(f"[ERROR] Failed to save files: {e}")

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

def get_file_type(filename):
    """Determine file type from extension"""
    if not filename or '.' not in filename:
        return 'file'
    
    ext = filename.lower().split('.')[-1]
    if ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']:
        return 'document'
    elif ext in ['jpg', 'jpeg', 'png', 'gif']:
        return 'image'
    elif ext in ['mp4', 'avi', 'mov']:
        return 'video'
    elif ext in ['py', 'java', 'js', 'html', 'css']:
        return 'code'
    else:
        return 'file'

def get_file_icon(filename):
    """Get icon for file type"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    icons = {
        'pdf': '📄', 'doc': '📄', 'docx': '📄', 'txt': '📄',
        'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
        'mp4': '🎥', 'avi': '🎥', 'mov': '🎥',
        'py': '🐍', 'java': '☕', 'js': '📜', 'html': '🌐', 'css': '🎨',
        'zip': '📦', 'rar': '📦',
    }
    return icons.get(ext, '📄')

def generate_file_id(filename):
    """Generate unique file ID"""
    timestamp = int(time.time() * 1000)
    unique_str = f"{filename}_{timestamp}_{random.randint(1000, 9999)}"
    return hashlib.md5(unique_str.encode()).hexdigest()[:12]

def is_authenticated():
    """Check if user is logged in"""
    return 'user_id' in session and 'username' in session

def require_auth():
    """Decorator to require authentication"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            if not is_authenticated():
                return jsonify({'success': False, 'error': 'Authentication required'}), 401
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

# ========== AUTHENTICATION ROUTES ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        email = data.get('email', '').strip()
        
        # Validation
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        if len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        users = load_users()
        for user in users:
            if user['username'].lower() == username.lower():
                return jsonify({'success': False, 'error': 'Username already exists'}), 400
        
        # Create new user
        new_user = {
            'id': f"user_{len(users) + 1:03d}",
            'username': username,
            'password': hashlib.sha256(password.encode()).hexdigest(),  # Hash password
            'email': email,
            'role': 'user',
            'created_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        save_users(users)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'role': new_user['role']
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        users = load_users()
        
        # Find user and verify password
        for user in users:
            if user['username'] == username:
                # Verify hashed password
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                if user['password'] == hashed_password:
                    # Set session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    
                    return jsonify({
                        'success': True,
                        'message': 'Login successful',
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'email': user.get('email', ''),
                            'role': user['role']
                        }
                    })
                else:
                    return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        return jsonify({'success': False, 'error': 'User not found'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Check authentication status"""
    if is_authenticated():
        return jsonify({
            'success': True,
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role')
            }
        })
    return jsonify({'success': True, 'authenticated': False})

# ========== PROTECTED FRONTEND ROUTES ==========
@app.route('/')
def index():
    """Serve the main cloud drive page (protected)"""
    if not is_authenticated():
        return send_file('login.html') if os.path.exists('login.html') else "Please login at /login.html"
    
    try:
        return send_file('cloud-drive.html')
    except:
        return "Cloud Drive - Logged in as " + session.get('username', 'User')

@app.route('/login.html')
def serve_login():
    """Serve login page"""
    try:
        return send_file('login.html')
    except:
        # Fallback login page
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cloud Drive Login</title>
            <style>
                body { font-family: Arial; padding: 40px; max-width: 400px; margin: 0 auto; }
                .login-box { border: 1px solid #ddd; padding: 30px; border-radius: 10px; }
                input { width: 100%; padding: 10px; margin: 10px 0; }
                button { background: #007bff; color: white; padding: 12px; border: none; width: 100%; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>Cloud Drive Login</h2>
                <div id="error" class="error"></div>
                <input type="text" id="username" placeholder="Username" value="admin">
                <input type="password" id="password" placeholder="Password" value="admin123">
                <button onclick="login()">Login</button>
                <p style="text-align:center; margin-top:20px;">Demo: admin / admin123</p>
            </div>
            <script>
                async function login() {
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    
                    const response = await fetch('/api/auth/login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({username, password})
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        window.location.href = '/';
                    } else {
                        document.getElementById('error').innerText = result.error || 'Login failed';
                    }
                }
            </script>
        </body>
        </html>
        """
        return html

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    try:
        return send_from_directory('.', filename)
    except:
        return jsonify({'error': 'File not found'}), 404

# ========== PROTECTED API ROUTES ==========
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    files = load_files()
    return jsonify({
        'status': 'healthy',
        'authenticated': is_authenticated(),
        'server': 'Cloud Drive API',
        'version': '3.0',
        'timestamp': datetime.now().isoformat(),
        'files_count': len(files),
        'nodes_count': len(NODES)
    })

@app.route('/api/nodes', methods=['GET'])
@require_auth()
def get_nodes():
    """Get all storage nodes (protected)"""
    return jsonify(NODES)

@app.route('/api/files', methods=['GET'])
@require_auth()
def get_files():
    """Get all uploaded files (protected)"""
    files = load_files()
    
    # Add missing fields and format data
    formatted_files = []
    for file in files:
        if not isinstance(file, dict):
            continue
            
        formatted = {
            'id': file.get('id', 'unknown'),
            'name': file.get('name', 'Unknown File'),
            'size': file.get('size', 0),
            'size_formatted': format_size(file.get('size', 0)),
            'upload_date': file.get('upload_date', 'Unknown'),
            'type': get_file_type(file.get('name', '')),
            'icon': get_file_icon(file.get('name', '')),
            'nodes': file.get('nodes', []),
            'download_url': f"/api/download/{file.get('id', '')}",
            'path': file.get('path', '')
        }
        formatted_files.append(formatted)
    
    return jsonify(formatted_files)

@app.route('/api/upload', methods=['POST'])
@require_auth()
def upload_file():
    """Handle file upload (protected)"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename:
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        # Get original filename
        original_filename = file.filename
        
        # Read file content to get size
        file_data = file.read()
        file_size = len(file_data)
        file.seek(0)
        
        # Generate unique ID
        file_id = generate_file_id(original_filename)
        
        # Create safe filename
        safe_filename = "".join(c for c in original_filename if c.isalnum() or c in ' ._-')
        if not safe_filename:
            safe_filename = f"file_{file_id}"
        
        # Create save path
        save_path = os.path.join(UPLOAD_FOLDER, f"{file_id}_{safe_filename}")
        
        # Save file
        file.save(save_path)
        print(f"[UPLOAD] File saved: {save_path} ({file_size} bytes)")
        
        # Distribute across 3 random nodes (simulation)
        distributed_nodes = random.sample([n['id'] for n in NODES], min(3, len(NODES)))
        
        # Create file metadata with user info
        file_meta = {
            'id': file_id,
            'name': original_filename,
            'size': file_size,
            'size_formatted': format_size(file_size),
            'upload_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': get_file_type(original_filename),
            'icon': get_file_icon(original_filename),
            'nodes': distributed_nodes,
            'path': save_path,
            'uploaded_by': session.get('username'),
            'user_id': session.get('user_id')
        }
        
        # Save to database
        files = load_files()
        files.append(file_meta)
        save_files(files)
        
        print(f"[UPLOAD] Success: {original_filename} uploaded by {session.get('username')}")
        
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file': file_meta,
            'total_files': len(files)
        })
        
    except Exception as e:
        print(f"[UPLOAD] Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/download/<file_id>', methods=['GET'])
@require_auth()
def download_file(file_id):
    """Download a file by ID (protected)"""
    try:
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
        return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        print(f"[DOWNLOAD] Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete/<file_id>', methods=['DELETE'])
@require_auth()
def delete_file(file_id):
    """Delete a file by ID (protected)"""
    try:
        files = load_files()
        file_found = None
        file_index = -1
        
        # Find the file
        for i, file in enumerate(files):
            if file.get('id') == file_id:
                # Check permission (admin or owner)
                if session.get('role') != 'admin' and file.get('user_id') != session.get('user_id'):
                    return jsonify({'success': False, 'error': 'Permission denied'}), 403
                
                file_found = file
                file_index = i
                break
        
        if not file_found:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Delete physical file
        file_path = file_found.get('path')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"[DELETE] Removed file: {file_path}")
        
        # Remove from database
        files.pop(file_index)
        save_files(files)
        
        print(f"[DELETE] Success: Deleted file {file_found.get('name')}")
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully',
            'deleted_file': file_found.get('name'),
            'remaining_files': len(files)
        })
        
    except Exception as e:
        print(f"[DELETE] Error: {str(e)}")
        return jsonify({'success': False, 'error': f'Delete failed: {str(e)}'}), 500

# ========== START APPLICATION ==========
if __name__ == '__main__':
    print("=" * 80)
    print("🔐 CLOUD DRIVE WITH AUTHENTICATION")
    print("=" * 80)
    print(f"📂 Upload Folder: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"🗃️  Database: {os.path.abspath(FILES_DB)}")
    print(f"👥 Users DB: {os.path.abspath(USERS_DB)}")
    print(f"🔗 Server URL: http://localhost:5001")
    print(f"🔐 Login URL: http://localhost:5001/login.html")
    print(f"🖥️  Storage Nodes: {len(NODES)}")
    
    # Initialize databases if needed
    if not os.path.exists(FILES_DB) or os.path.getsize(FILES_DB) == 0:
        save_files([])
        print("📝 Created new files database")
    
    if not os.path.exists(USERS_DB) or os.path.getsize(USERS_DB) == 0:
        save_users(DEFAULT_USERS)
        print("👥 Created users database")
        print("   Default users created:")
        print("   - admin / admin123 (Administrator)")
        print("   - user1 / password123 (Regular user)")
    
    files = load_files()
    users = load_users()
    print(f"📊 Existing Files: {len(files)}")
    print(f"👤 Registered Users: {len(users)}")
    
    print("\n" + "-" * 80)
    print("📡 AVAILABLE ENDPOINTS:")
    print("  AUTH:")
    print("    POST /api/auth/register - Register new user")
    print("    POST /api/auth/login    - Login")
    print("    POST /api/auth/logout   - Logout")
    print("    GET  /api/auth/check    - Check auth status")
    
    print("\n  PROTECTED API:")
    print("    GET  /api/health        - System Health")
    print("    GET  /api/nodes         - Storage Nodes")
    print("    GET  /api/files         - List Files")
    print("    POST /api/upload        - Upload File")
    print("    GET  /api/download/<id> - Download File")
    print("    DELETE /api/delete/<id> - Delete File")
    print("-" * 80)
    print("\n⚡ Starting server... Press Ctrl+C to stop")
    print("=" * 80)
    
    try:
        app.run(debug=True, port=5001, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n💥 Server error: {e}")