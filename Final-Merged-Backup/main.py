import sys
import os
import subprocess

def run_cloud_drive():
    """Run the cloud drive Flask application"""
    print("=" * 60)
    print("CLOUD DRIVE SYSTEM")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Change to ui directory
    ui_dir = os.path.join(os.path.dirname(__file__), 'ui')
    os.chdir(ui_dir)
    
    # Run the Flask app
    subprocess.run([sys.executable, 'api.py'])

def run_calculator():
    """Run the calculator system"""
    print("=" * 60)
    print("CALCULATOR SYSTEM")
    print("=" * 60)
    print("This feature is under development...")
    print("=" * 60)

if __name__ == "__main__":
    print("Welcome to Distributed Cloud System")
    print("\n1. Cloud Drive (File Storage)")
    print("2. Calculator (Coming Soon)")
    
    choice = input("\nChoose option (1): ").strip()
    
    if choice == "2":
        run_calculator()
    else:
        run_cloud_drive()
        cd
        