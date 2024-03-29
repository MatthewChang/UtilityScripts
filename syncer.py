import os
import time
import fnmatch
import subprocess
import yaml
import argparse
from functools import partial
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

def file_change_callback(config):
    print("Syncing")
    command = build_command(config)
    print(" ".join(command))
    subprocess.call(command)
    print("Waiting for changes...")

def build_command(config,down=False):
    remote_server = config['remote_server'] 
    remote_folder = config['remote_folder']
    include_statements = [f'--include={inc}' for inc in config['include']]

    # exclude from gitignore
    # subprocess.call(["rsync", "-avzu", "--compress", "--size-only", *extra_patterns,"--exclude-from", ".gitignore", ".", f"{remote_folder}"])

    # this order is required
    # include all directories and any file/glob specified in the config
    extra_patterns = ['--include=*/', *include_statements, '--exclude=*']
    # the -m flag stops empty directories from being created
    flags = '-avzum'
    # dry run only
    if config['dry']:
        flags += 'n'
    # command = ["rsync",flags, "--compress", "--size-only", *extra_patterns]
    command = ["rsync",flags, "--compress", *extra_patterns]

    if down:
        command += [f"{remote_server}:{remote_folder}/",'.']
    else:
        command += [".", f"{remote_server}:{remote_folder}"]
    return command

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

def monitor_directory_changes(config,directory, ignore_patterns=None):
    callback = partial(file_change_callback, config)
    event_handler = FileChangeHandler(callback, ignore_patterns)
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

def sync_all_files(config,ignore_patterns=None):
    # Pull down the .gitignore file from the remote server
    subprocess.call(["rsync", "-avz", f"{remote_server}:{remote_folder}/.gitignore", "."])

    # Perform the sync, excluding files based on the pulled .gitignore
    command = build_command(config,True)
    print(" ".join(command))
    subprocess.call(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Watch for file changes and perform sync")
    parser.add_argument('-c',"--config", default='.sync.yml', help="config file")
    parser.add_argument("--sync-all", action="store_true", help="Perform a one-time sync of all files")
    parser.add_argument('-s',"--remote-server", default=None, help="Remote server to sync to")
    parser.add_argument('-f',"--remote-folder", default=None, help="Remote folder to sync to")
    parser.add_argument('-n',"--dry-run", action="store_true")
    args = parser.parse_args()

    current_directory = os.getcwd()
    ignore_patterns = load_ignore_patterns()

    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    remote_server = config.get("remote_server")
    remote_folder = config.get("remote_folder")
    if args.remote_server:
        remote_server = args.remote_server
    if args.remote_folder:
        remote_folder = args.remote_folder
    config = {'remote_server': remote_server, 'remote_folder': remote_folder,'dry': args.dry_run,'include': config.get('include',[])}
    if args.sync_all:
        sync_all_files(config,ignore_patterns)
    else:
        monitor_directory_changes(config,current_directory, ignore_patterns)

