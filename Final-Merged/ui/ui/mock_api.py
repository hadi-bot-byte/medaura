from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Mock data
mock_files = [
    {"id": "1", "name": "project_document.pdf", "size": 5242880, "upload_date": "2024-01-15", "nodes": ["node1", "node2", "node3"]},
    {"id": "2", "name": "presentation.pptx", "size": 10485760, "upload_date": "2024-01-14", "nodes": ["node2", "node3", "node4"]},
    {"id": "3", "name": "data_analysis.csv", "size": 2097152, "upload_date": "2024-01-13", "nodes": ["node1", "node4", "node5"]},
    {"id": "4", "name": "code_backup.zip", "size": 15728640, "upload_date": "2024-01-12", "nodes": ["node3", "node4", "node5"]},
]

# Login endpoint
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    if username and password:
        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": username
        })
    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    })

# Get files endpoint
@app.route('/api/files', methods=['GET'])
def get_files():
    files_with_icons = []
    for file in mock_files:
        file_copy = file.copy()
        # Add icon based on file type
        if file["name"].endswith(".pdf"):
            file_copy["icon"] = "📕"
        elif file["name"].endswith(".pptx"):
            file_copy["icon"] = "📊"
        elif file["name"].endswith(".csv"):
            file_copy["icon"] = "📈"
        elif file["name"].endswith(".zip"):
            file_copy["icon"] = "📦"
        else:
            file_copy["icon"] = "📄"
        
        # Format size
        size = file["size"]
        if size < 1024*1024:
            file_copy["size_formatted"] = f"{size/1024:.1f} KB"
        elif size < 1024*1024*1024:
            file_copy["size_formatted"] = f"{size/(1024*1024):.1f} MB"
        else:
            file_copy["size_formatted"] = f"{size/(1024*1024*1024):.1f} GB"
        
        files_with_icons.append(file_copy)
    
    return jsonify(files_with_icons)

# Calculate endpoint
@app.route('/api/calculate', methods=['POST'])
def calculate():
    data = request.json
    num1 = data.get('num1', 0)
    num2 = data.get('num2', 1)
    operation = data.get('operation', 'add')
    
    result = 0
    if operation == 'add':
        result = num1 + num2
    elif operation == 'sub':
        result = num1 - num2
    elif operation == 'mul':
        result = num1 * num2
    elif operation == 'div':
        result = num1 / num2 if num2 != 0 else 0
    elif operation == 'mod':
        result = num1 % num2
    
    return jsonify({
        "num1": num1,
        "num2": num2,
        "operation": operation,
        "result": result
    })

# Upload endpoint (mock)
@app.route('/api/upload', methods=['POST'])
def upload():
    return jsonify({
        "success": True,
        "message": "File uploaded successfully",
        "nodes": ["node1", "node2", "node3", "node4", "node5"]
    })

# Download endpoint (mock)
@app.route('/api/download/<file_id>', methods=['GET'])
def download(file_id):
    # In a real app, this would send the actual file
    return jsonify({
        "success": True,
        "message": f"Downloading file {file_id}"
    })

# Delete endpoint (mock)
@app.route('/api/delete/<file_id>', methods=['DELETE'])
def delete(file_id):
    return jsonify({
        "success": True,
        "message": f"File {file_id} deleted"
    })

if __name__ == '__main__':
    print("Starting mock API server on http://localhost:5001")
    print("Access the frontend by opening your HTML file in a browser")
    print("Default login: admin / admin123")
    app.run(debug=True, port=5001)