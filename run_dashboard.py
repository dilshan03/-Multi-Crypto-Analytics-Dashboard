#!/usr/bin/env python3
"""
Startup script for the Crypto Dashboard project.
This script provides easy commands to run different components.
"""

import sys
import subprocess
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Running: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with error: {e}")
        return False

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("""
🚀 Crypto Dashboard - Startup Script

Usage: python run_dashboard.py <command>

Available commands:
  init        - Install dependencies and fetch initial data
  fetch       - Fetch cryptocurrency data
  analytics   - Generate technical analytics
  dashboard   - Start the web dashboard
  scheduler   - Start automated data collection
  all         - Run fetch, analytics, and start dashboard

Examples:
  python run_dashboard.py init
  python run_dashboard.py dashboard
  python run_dashboard.py scheduler
        """)
        return
    
    command = sys.argv[1].lower()
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    if command == "init":
        print("🔧 Initializing Crypto Dashboard...")
        
        # Install dependencies
        if not run_command("pip install -r requirements.txt", "Installing dependencies"):
            return
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        # Fetch initial data
        if not run_command("python scripts/fetch_data.py", "Fetching initial cryptocurrency data"):
            return
        
        # Generate analytics
        if not run_command("python scripts/analytics.py", "Generating technical analytics"):
            return
        
        print("\n🎉 Initialization complete!")
        print("You can now run: python run_dashboard.py dashboard")
    
    elif command == "fetch":
        run_command("python scripts/fetch_data.py", "Fetching cryptocurrency data")
    
    elif command == "analytics":
        run_command("python scripts/analytics.py", "Generating technical analytics")
    
    elif command == "dashboard":
        print("\n🌐 Starting Crypto Dashboard...")
        print("Dashboard will open in your browser at: http://localhost:8501")
        print("Press Ctrl+C to stop the dashboard")
        run_command("streamlit run dashboard/app.py", "Starting web dashboard")
    
    elif command == "scheduler":
        print("\n⏰ Starting automated data collection...")
        print("Data will be collected every 5 minutes")
        print("Press Ctrl+C to stop the scheduler")
        run_command("python scripts/scheduler.py", "Starting automated scheduler")
    
    elif command == "all":
        print("🚀 Running complete dashboard setup...")
        
        # Fetch data
        if not run_command("python scripts/fetch_data.py", "Fetching cryptocurrency data"):
            return
        
        # Generate analytics
        if not run_command("python scripts/analytics.py", "Generating technical analytics"):
            return
        
        # Start dashboard
        print("\n🌐 Starting Crypto Dashboard...")
        print("Dashboard will open in your browser at: http://localhost:8501")
        run_command("streamlit run dashboard/app.py", "Starting web dashboard")
    
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: init, fetch, analytics, dashboard, scheduler, all")

if __name__ == "__main__":
    main()
