# start_ollama.py
# Run with: python start_ollama.py

import subprocess
import sys
import time

import requests


def is_ollama_running() -> bool:
    """Check if Ollama is already running on the default port."""
    try:
        response = requests.get("http://127.0.0.1:11434/api/version", timeout=2)
        return response.status_code == 200
    except:
        return False


def run_command(cmd, description):
    """Run a command with proper UTF-8 encoding to avoid Windows console errors."""
    print(f"   {description} ...")
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',      # This prevents the UnicodeDecodeError
            timeout=300
        )
        if result.returncode == 0:
            print(f"   ✅ {description} completed")
            return True
        else:
            print(f"   ⚠️  {description} had warnings: {result.stderr.strip()[:200]}...")
            return False
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  Timeout during {description}")
        return False
    except Exception as e:
        print(f"   ❌ Error during {description}: {e}")
        return False


def start_ollama():
    print("🚀 Ollama Manager\n")

    # Check if Ollama is already running
    if is_ollama_running():
        print("✅ Ollama server is already running.")
    else:
        print("Starting Ollama server in background...")
        try:
            subprocess.Popen(
                ["ollama", "serve"],
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            print("   Ollama server started.")
            time.sleep(4)
        except FileNotFoundError:
            print("❌ Error: 'ollama' command not found. Make sure Ollama is installed and in your PATH.")
            sys.exit(1)

    # Preload both models
    models = ["qwen2.5:7b", "qwen2.5vl:7b"]

    for model in models:
        run_command(["ollama", "pull", model], f"Preloading {model}")

    print("\n🎉 Ollama is ready with both models loaded!")
    print("   You can now run your classification pipeline.")
    print("   Press Ctrl+C to stop the server when you're done.\n")

    # Keep the script running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Stopping Ollama server...")
        print("   Server stopped.")


if __name__ == "__main__":
    start_ollama()