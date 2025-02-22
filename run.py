import time
import os
import subprocess
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

running = True
file_to_watch = os.path.abspath("/workspaces/Block-Chain/button.py")  # Đường dẫn tuyệt đối

# Kiểm tra xem file button.py có tồn tại hay không
if not os.path.isfile(file_to_watch):
    print(f"❌ File {file_to_watch} does not exist.")
    exit(1)

# Kiểm tra xem file button.py có thể chạy được hay không
try:
    result = subprocess.run(["python3", file_to_watch], capture_output=True, text=True)
    print(f"✅ File {file_to_watch} is executable.")
    print(result.stdout)
    print(result.stderr)
except Exception as e:
    print(f"❌ Error running {file_to_watch}: {e}")
    exit(1)

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"📂 File changed: {event.src_path}")  # Debug

        if event.is_directory:  # Bỏ qua thư mục
            return

        if file_to_watch in event.src_path:
            print(f"🚀 Restarting button.py...")
            try:
                print(f"🔄 Running {file_to_watch}...")
                result = subprocess.run(["python3", file_to_watch], capture_output=True, text=True)
                print(f"stdout: {result.stdout}")  # Debug
                print(f"stderr: {result.stderr}")  # Debug
                print(f"✅ Finished running {file_to_watch}")
            except Exception as e:
                print(f"❌ Error running button.py: {e}")

def stop_running():
    global running
    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        running = False

if __name__ == "__main__":
    path = os.path.dirname(file_to_watch)  # Lấy thư mục chứa button.py
    print(f"📂 Watching directory: {path}")  # Debug
    print(f"📂 Watching file: {file_to_watch}")  # Debug
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()

    print("✅ Watchdog is running, waiting for file changes...")  # Debug

    threading.Thread(target=stop_running, daemon=True).start()

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("🛑 Watchdog stopped.")