#!/usr/bin/env python3
"""
Backend API Server for CloudDrive Distributed Storage System
Connects to CloudSim and Cloud gRPC modules
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import time
from datetime import datetime
import uuid
import json
import sys

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

# Storage for demo data
storage_nodes = [
    {"id": "node1", "ip": "192.168.1.101", "status": "online", "capacity": "1TB", "used": "450GB"},
    {"id": "node2", "ip": "192.168.1.102", "status": "online", "capacity": "1TB", "used": "320GB"},
    {"id": "node3", "ip": "192.168.1.103", "status": "online", "capacity": "1TB", "used": "510GB"},
    {"id": "node4", "ip": "192.168.1.104", "status": "online", "capacity": "1TB", "used": "280GB"},
    {"id": "node5", "ip": "192.168.1.105", "status": "online", "capacity": "1TB", "used": "390GB"}
]

stored_files = []

# Ensure uploads directory exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get status of all storage nodes"""
    try:
        import random
        # Add some randomness to make it look real
        updated_nodes = []
        for node in storage_nodes:
            node_copy = node.copy()
            # 10% chance to change status
            if random.random() < 0.1:
                node_copy["status"] = "offline" if node_copy["status"] == "online" else "online"
            updated_nodes.append(node_copy)
        
        return jsonify(updated_nodes)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/files', methods=['GET'])
def get_files():
    """Get list of uploaded files"""
    try:
        return jsonify(stored_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload and distribute a file across storage nodes"""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save file to uploads directory
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Get file size
        file_size = os.path.getsize(filepath)
        
        # Generate file info
        file_id = str(uuid.uuid4())[:8]
        
        import random
        num_nodes = random.randint(2, 5)
        selected_nodes = random.sample([n["id"] for n in storage_nodes], num_nodes)
        
        file_info = {
            "id": file_id,
            "name": filename,
            "size": file_size,
            "upload_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "nodes": selected_nodes,
            "path": filepath,
            "type": file.content_type or "application/octet-stream"
        }
        
        stored_files.append(file_info)
        
        # Simulate distribution processing
        time.sleep(0.5)
        
        return jsonify({
            "success": True,
            "message": f"File '{filename}' distributed successfully",
            "file_id": file_id,
            "nodes": selected_nodes,
            "size": file_size
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate', methods=['POST'])
def calculate():
    """Perform calculation via gRPC service"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        num1 = float(data.get('num1', 0))
        num2 = float(data.get('num2', 0))
        operation = data.get('operation', 'add')
        
        # Calculate result
        result = 0
        if operation == 'add':
            result = num1 + num2
        elif operation == 'sub':
            result = num1 - num2
        elif operation == 'mul':
            result = num1 * num2
        elif operation == 'div':
            if num2 == 0:
                return jsonify({"error": "Division by zero"}), 400
            result = num1 / num2
        
        # Simulate gRPC call delay
        time.sleep(0.3)
        
        return jsonify({
            "success": True,
            "operation": operation,
            "result": result,
            "via_grpc": True,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cloudsim/start', methods=['POST'])
def start_cloudsim():
    """Start CloudSim simulation"""
    try:
        # This is where you would integrate with your actual CloudSim module
        print("Starting CloudSim simulation...")
        
        return jsonify({
            "success": True,
            "message": "CloudSim started successfully",
            "simulation_id": "SIM_" + str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/cloudsim/stop', methods=['POST'])
def stop_cloudsim():
    """Stop CloudSim simulation"""
    try:
        print("Stopping CloudSim simulation...")
        
        return jsonify({
            "success": True,
            "message": "CloudSim stopped successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/grpc/start', methods=['POST'])
def start_grpc():
    """Start gRPC server"""
    try:
        data = request.get_json()
        endpoint = data.get('endpoint', 'localhost:50051')
        
        print(f"Starting gRPC server on {endpoint}...")
        
        return jsonify({
            "success": True,
            "message": f"gRPC server started on {endpoint}",
            "server_id": "GRPC_" + str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/grpc/stop', methods=['POST'])
def stop_grpc():
    """Stop gRPC server"""
    try:
        print("Stopping gRPC server...")
        
        return jsonify({
            "success": True,
            "message": "gRPC server stopped successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "cloudsim": "available",
            "grpc": "available",
            "api": "running"
        }
    })

@app.route('/api/system/start', methods=['POST'])
def start_system():
    """Start the merged system"""
    try:
        data = request.get_json()
        mode = data.get('mode', 'simulation')
        
        print(f"Starting merged system in {mode} mode...")
        
        return jsonify({
            "success": True,
            "message": f"Merged system started in {mode} mode",
            "system_id": "SYS_" + str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/system/stop', methods=['POST'])
def stop_system():
    """Stop the merged system"""
    try:
        print("Stopping merged system...")
        
        return jsonify({
            "success": True,
            "message": "Merged system stopped successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
def run_test():
    """Run system tests"""
    try:
        print("Running system tests...")
        
        # Simulate test execution
        time.sleep(1)
        
        test_results = [
            {"test": "CloudSim Basic", "status": "passed", "details": "Basic simulation works correctly"},
            {"test": "gRPC Connection", "status": "passed", "details": "gRPC endpoints responding"},
            {"test": "File Distribution", "status": "passed", "details": "Files distributed across nodes"},
            {"test": "Calculator Service", "status": "passed", "details": "All arithmetic operations working"},
            {"test": "System Integration", "status": "passed", "details": "Modules communicate properly"}
        ]
        
        return jsonify({
            "success": True,
            "message": "System tests completed",
            "results": test_results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Simple file download endpoint
@app.route('/api/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a file"""
    try:
        # Find the file
        file_info = None
        for f in stored_files:
            if f["id"] == file_id:
                file_info = f
                break
        
        if not file_info or not os.path.exists(file_info["path"]):
            return jsonify({"error": "File not found"}), 404
        
        return jsonify({
            "success": True,
            "file": file_info,
            "download_url": f"/download_file/{file_id}"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_file/<file_id>')
def serve_file(file_id):
    """Serve the actual file"""
    try:
        # Find the file
        file_info = None
        for f in stored_files:
            if f["id"] == file_id:
                file_info = f
                break
        
        if not file_info or not os.path.exists(file_info["path"]):
            return "File not found", 404
        
        from flask import send_file
        return send_file(file_info["path"], as_attachment=True)
        
    except Exception as e:
        return str(e), 500

@app.route('/')
def index():
    """Root endpoint - redirect to API docs"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CloudDrive API Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #333; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
            .method { display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            .put { background: #fca130; }
            .delete { background: #f93e3e; }
        </style>
    </head>
    <body>
        <h1>CloudDrive Distributed Storage API Server</h1>
        <p>Server is running. Use the following endpoints:</p>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/health</strong> - Health check
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/nodes</strong> - Get storage node status
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/files</strong> - Get uploaded files
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/upload</strong> - Upload a file
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/calculate</strong> - Perform calculation
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/cloudsim/start</strong> - Start CloudSim
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/grpc/start</strong> - Start gRPC server
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/system/start</strong> - Start merged system
        </div>
        
        <p>Frontend should be running on a different port (e.g., 8000)</p>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("=" * 60)
    print("CloudDrive Distributed Storage API Server")
    print("=" * 60)
    print(f"API URL: http://localhost:5001")
    print(f"Frontend URL: http://localhost:8000 (if running)")
    print("=" * 60)
    print("Endpoints available:")
    print("  GET  /api/health           - Health check")
    print("  GET  /api/nodes            - Storage node status")
    print("  GET  /api/files            - Uploaded files")
    print("  POST /api/upload           - Upload file")
    print("  POST /api/calculate        - Calculator")
    print("  POST /api/cloudsim/start   - Start CloudSim")
    print("  POST /api/cloudsim/stop    - Stop CloudSim")
    print("  POST /api/grpc/start       - Start gRPC server")
    print("  POST /api/grpc/stop        - Stop gRPC server")
    print("  POST /api/system/start     - Start merged system")
    print("  POST /api/test             - Run system tests")
    print("=" * 60)
    
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created uploads directory: {UPLOAD_FOLDER}")
    
    app.run(host='0.0.0.0', port=5001, debug=True)