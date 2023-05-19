import os
import time
import fnmatch
import subprocess
import yaml
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# For increased speed, setup an ssh tunnel to the target server directly using SSH multiplexing
# https://blog.scottlowe.org/2015/12/11/using-ssh-multiplexing/
# this way rsync will not redo the ssh handshake every time
# but just reuse an exising connection
# add this to your ~/.ssh/config
# Host *
#  ControlMaster auto
#  ControlPath ~/.ssh/cm-%r@%h:%p
# then if you start a connection which is held open with with `ssh -vN user@host`
# in another terminal if you `rsync file user@host:file`
# you can see the the first connection is reused, and should
# be much faster to connect

config_file = '.sync.yml'

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback, ignore_patterns=None):
        super().__init__()
        self.callback = callback
        self.ignore_patterns = ignore_patterns or []

    def should_ignore(self, file_path):
        print(self.ignore_patterns)
        for pattern in self.ignore_patterns:
            # deosn't really work properly right now
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def on_modified(self, event):
        rel_path = os.path.relpath(event.src_path)
        if not event.is_directory and not self.should_ignore(rel_path):
            print(event)
            print(event.src_path)
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
    ignore_patterns = ['.git/**/*','.git/*']
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
    observer.schedule(event_handler, directory, recursive=True)
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
    subprocess.call(["rsync", "-avzu", "--exclude-from", ".gitignore", f"{remote_server}:{remote_folder}/", "."])

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

