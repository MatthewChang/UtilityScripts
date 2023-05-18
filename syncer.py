import os
import time
import fnmatch
import subprocess
import yaml
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

config_file = '.sync.yml'

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback, ignore_patterns=None):
        super().__init__()
        self.callback = callback
        self.ignore_patterns = ignore_patterns or []

    def should_ignore(self, file_path):
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def on_modified(self, event):
        if not event.is_directory and not self.should_ignore(event.src_path):
            self.callback()

def file_change_callback():
    print("Syncing")
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    remote_server = config.get("remote_server")
    remote_folder = config.get("remote_folder")
    subprocess.call(["rsync", "-avzu", "--compress", "--size-only", "--exclude-from", ".gitignore", ".", f"{remote_server}:{remote_folder}"])

    print("Waiting for changes...")

def load_ignore_patterns():
    ignore_patterns = []
    gitignore_file = os.path.join(os.getcwd(), '.gitignore')
    if os.path.isfile(gitignore_file):
        with open(gitignore_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignore_patterns.append(line)
    return ignore_patterns

def monitor_directory_changes(directory, ignore_patterns=None):
    event_handler = FileChangeHandler(file_change_callback, ignore_patterns)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()

    try:
        print("Waiting for changes...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

def sync_all_files(ignore_patterns=None):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    remote_server = config.get("remote_server")
    remote_folder = config.get("remote_folder")

    # Pull down the .gitignore file from the remote server
    subprocess.call(["rsync", "-avz", f"{remote_server}:{remote_folder}/.gitignore", "."])

    # Perform the sync, excluding files based on the pulled .gitignore
    subprocess.call(["rsync", "-avzu", "--exclude-from", ".gitignore", f"{remote_server}:{remote_folder}", "."])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch for file changes and perform sync")
    parser.add_argument("--sync-all", action="store_true", help="Perform a one-time sync of all files")
    args = parser.parse_args()

    current_directory = os.getcwd()
    ignore_patterns = load_ignore_patterns()

    if args.sync_all:
        sync_all_files(ignore_patterns)
    else:
        monitor_directory_changes(current_directory, ignore_patterns)

