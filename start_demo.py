#!/usr/bin/env python3
"""
Demo startup script for EPV Research Platform
Starts both the FastAPI backend and serves the React frontend
"""
import subprocess
import sys
import time
from pathlib import Path


def start_api_server():
    """Start the FastAPI backend server"""
    print("🚀 Starting FastAPI backend server...")
    api_process = subprocess.Popen(
        [sys.executable, "src/main.py", "api", "--port", "8000"],
        cwd=Path(__file__).parent,
    )
    return api_process


def start_frontend():
    """Start the React frontend development server"""
    print("🎨 Starting React frontend...")
    frontend_dir = Path(__file__).parent / "frontend"
    if not frontend_dir.exists():
        print("❌ Frontend directory not found. Please run the setup first.")
        return None

    frontend_process = subprocess.Popen(["npm", "start"], cwd=frontend_dir)
    return frontend_process


def main():
    """Main startup function"""
    print("🏁 Starting EPV Research Platform Demo...")
    print("=" * 50)

    try:
        # Start API server
        api_process = start_api_server()
        time.sleep(3)  # Give API server time to start

        # Start frontend
        frontend_process = start_frontend()

        if frontend_process is None:
            print("❌ Failed to start frontend")
            api_process.terminate()
            return 1

        print("\n✅ Both servers started successfully!")
        print("📊 API Server: http://localhost:8000")
        print("🌐 Frontend: http://localhost:3000")
        print("\nPress Ctrl+C to stop both servers")

        # Wait for user interrupt
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")

    except Exception as e:
        print(f"❌ Error starting servers: {e}")
        return 1

    finally:
        # Clean up processes
        try:
            if "api_process" in locals():
                api_process.terminate()
                api_process.wait(timeout=5)
        except:
            pass

        try:
            if "frontend_process" in locals():
                frontend_process.terminate()
                frontend_process.wait(timeout=5)
        except:
            pass


if __name__ == "__main__":
    exit(main())
