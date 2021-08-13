#! python -m flask
from flask import Flask, send_from_directory, copy_current_request_context
import os
from watchdog.observers import Observer 
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from queue import Queue
from inotify_simple import INotify, flags
watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF


app = Flask(__name__)
script = """ let selected = null; 
let evtSource;
function select(ind){
    if (ind < 0) {
        ind = 0
    }
    if (ind >= paths.length) {
        ind = paths.length - 1
    }
    $("#item"+selected).css('background','white')
    $("#item"+ind).css('background','red')
    selected=ind
    $("#display").attr('src',paths[ind])
    
    // window.location.hash=ind
    history.replaceState(undefined, undefined,"#"+ind)
    let pageTop = $(window).scrollTop();
    let pageBottom = pageTop + window.innerHeight;
    let elementTop = $("#item"+ind).offset().top;
    let elementBottom = elementTop + $("#item"+ind).height();
    if (elementTop < pageTop) {
       $(window).scrollTop(elementTop)
    } else if (elementBottom > pageBottom) {
       $(window).scrollTop(elementBottom-window.innerHeight)
    }

    if (evtSource) {
        evtSource.close()
    }
    evtSource = new EventSource("listen"+paths[ind]);
    evtSource.onmessage = function(event) {
      console.log(event.data)
    }


}
$(document).ready(function(){
    select(parseInt(window.location.hash.substr(1)))
})
document.onkeydown = function(e) {
    switch(e.which) {
        case 37: // left
        break;

        case 38: // up
        select(selected-1)
        break;

        case 39: // right
        break;

        case 40: // down
        select(selected+1)
        break;
        default: return; // exit this handler for other keys
    }
    e.preventDefault(); // prevent the default action (scroll / move caret)
};
"""

image_extensions = ['png','jpg','jpeg','gif']
from flask import request, Response
import time
import pyinotify

wm = pyinotify.WatchManager()  # Watch Manager
class EventHandler(pyinotify.ProcessEvent):
    def __init__(self):
        super(EventHandler, self).__init__()
        self.queue = Queue()
    def process_IN_MODIFY(self, event):
        print("MODIFY:", event.pathname)
        self.queue.put(event.pathname)

# class EventHandler(FileSystemEventHandler):
    # def __init__(self):
        # super(EventHandler, self).__init__()
        # self.queue = Queue()
    # def on_modified(self, event):
        # super(EventHandler, self).on_modified(event)
        # print(event)
        # print("Modified %s", event.src_path)
        # self.queue.put(event.src_path,block=False)

@app.route("/listen")
def listen():
    path = request.args.get('path')

    # dirPath = os.path.dirname(path)
    # observer = PollingObserver()
    # # observer = Observer()
    # handler = EventHandler()
    # # observer.schedule(handler, '.'+request.args.get('path'))
    # print(dirPath)
    # observer.schedule(handler, '.'+dirPath)
    # observer.start()
    def stream():
        inotify = INotify()
        handler = EventHandler()
        dirPath = os.path.dirname(path)
        basePath = os.path.basename(path)
        wd = inotify.add_watch('.'+dirPath, flags.MODIFY)
        print(wd)
        try:
            while True:
                for event in inotify.read():
                    print(event)
                    for flag in flags.from_mask(event.mask):
                        print('    ' + str(flag))
                        if event.name == basePath:
                            yield ('data: {"abc": %s}\n\n' % (event.name))
                # time.sleep(5)
                # yield ('data: {"abc": test}\n\n' )
        except GeneratorExit:
            print('closed:', path)
            inotify.rm_watch(wd)
            del inotify
    return Response(stream(), mimetype='text/event-stream')

@app.route("/")
def hello_world():
    path = request.args.get('path')
    print('path: ',path)
    if path is None or os.path.isdir('./'+path):
        if path is None:
            path = ""
    
        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        res = f"<html><head><script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js\"></script><script src=\"https://gitcdn.link/repo/litera/jquery-scrollintoview/master/jquery.scrollintoview.min.js\"></script><script>{script}</script><title>{path}</title></head>"

        files = sorted(os.listdir('./'+path))
        if len(path) == 0:
            root_path = ''
        else:
            root_path = f'{path}'
        res += '<body style="display: flex"><div id="list">'
        res += f'<h3>{os.getcwd()}/{path}</h3>'
        for i,fil in enumerate(files):
            onclick =f"onclick=\"select({i})\""
            res += f'<p class="item" {onclick} style="background: white; margin: 0 0 0 0; padding: 5 25 5 10" id="item{i}"><a href="/?path={root_path}/{fil}">{fil}</a></p>'
        res += '</div>'
        res += f'<div><img id="display" style="position: fixed" src=""/></div>'
        paths = ','.join([f'"?path={root_path}/{fil}"' for fil in files])
        end_script = f"let paths = [{paths}]"
        res += f"<script>{end_script}</script></body></html>"
        return res
    else:
        print(os.path.dirname(path),os.path.basename(path))
        return send_from_directory(os.getcwd()+os.path.dirname(path),os.path.basename(path))


import threading

# def thread_function():
    # while True:
        # for event in inotify.read():
            # print(event)
            # for flag in flags.from_mask(event.mask):
                # print('    ' + str(flag))

# x = threading.Thread(target=thread_function)
# x.start()