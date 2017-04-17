import argparse
import os
import json
from subprocess import Popen
import subprocess
import shlex


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, WebKit, Vte, GLib, GObject


class Command:
    def __init__(self, context):
        self.context = context
        if self.context['env'] is None:
            self.context['env'] = []

    def _cwd(self):
        return self.context['cwd']

    def _env(self):
        return self.context['env']

    def parse_input(self, raw_input):
        pass

    def execute(self, parsed_input):
        pass

    def display_output(self, parsed_output):
        pass

def parse_fileinput(cwd, string):
    return os.path.join(cwd, string)


class RenderedCommand(Command):
    def display_output(self, parsed_output):
        mime_type = parsed_output['mimeType']
        sub_type = parsed_output['subtype']
        data = parsed_output['data']

class Ls(Command):

    def parse_input(self, raw_input):
        return list(map(
            (lambda path: parse_fileinput(self._cwd(), path)),
            raw_input.split(" ")
            ))

    def execute(self, parsed_input):
        folder = None
        if len(parsed_input) == 0:
            folder = "."
        else:
            folder = parsed_input[0]
        contents =  os.listdir(folder)
        def map_entry(entry):
            path = os.path.join(folder, entry)
            type = None
            if os.path.isfile(path):
                type = "file"
            elif os.path.isdir(path):
                type = "dir"
            elif os.path.islink(path):
                type = "link"
            elif os.path.ismount(path):
                type = "mount"
            else:
                type = "none"
            return {
                "name": entry,
                "type": type
            }
        with_types = map(map_entry, contents)
        return with_types


    def display_output(self, parsed_output):
        icon_types = {
            "file": Gtk.STOCK_FILE,
            "dir": Gtk.STOCK_DIRECTORY,
            "link": Gtk.STOCK_GO_UP,
            "mount": Gtk.STOCK_HARDDISK,
            "none": Gtk.STOCK_DIALOG_QUESTION
        }
        builder = Gtk.Builder()
        builder.add_from_file("process.glade")
        flow = builder.get_object("flow")
        for entry in parsed_output:
            entry_view = Gtk.HBox()
            icon = Gtk.Image(stock=icon_types[entry["type"]])
            entry_view.pack_start(icon, False, False, 0)
            entry_view.pack_start(Gtk.Label(entry["name"]), False, False, 0)
            flow.insert(entry_view, -1)
        return flow

class Image(Command):
    def parse_input(self, file):
        return {
            "file": parse_fileinput(self._cwd(), file)
        }

    def execute(self, file):
        return file

    def display_output(self, file):
        return Gtk.Image.new_from_file(file['file'])

class Cd(Command):
    def parse_input(self, file):
        return {
            "file": parse_fileinput(self._cwd(), file)
        }

    def execute(self, file):
        if os.path.isdir(file["file"]):
            self.context['cwd'] = file['file']
        else:
            return {"error": "Folder does not exist"}
        return {"error": None, "file": file}

    def display_output(self, output):
        if output["error"] is None:
            return Gtk.Label("")
        return Gtk.Label(output["error"])

class Web(Command):
    def parse_input(self, url):
        if url.startswith("http://") or url.startswith("https://"):
            return {
                "url": url
            }
        else:
            filepath = parse_fileinput(self._cwd(), url)
            if os.path.isfile(filepath):
                return {
                    "url": "file:///"+filepath
                }
            else:
                return {
                    "url": "http://"+url
                }

    def execute(self, url):
        return url

    def display_output(self, output):
        webview =  WebKit.WebView()
        webview.load_uri(output['url'])
        return webview



class SimpleShellCommand(Command):

    def parse_input(self, raw_input):
        return raw_input

    def execute(self, parsed_input):
        execution = Popen(parsed_input,
            shell=True,
            stdout=subprocess.PIPE,
            cwd=self._cwd())
        (output, err) = execution.communicate(timeout=1000)
        if output is None:
            return {
                "success": False,
                "error": "Error"
            }
        return {
            "output": output.decode("utf-8"),
            "success": err is None
            }

    def display_output(self, parsed_output):
        builder = Gtk.Builder()
        builder.add_from_file("process.glade")
        textview = builder.get_object("textview")

        output_text = ""
        if parsed_output["success"]:
            output_text = parsed_output["output"]
        else:
            output_text = parsed_output["error"]

        textview.get_buffer().set_text(output_text)
        return textview;

class Bash(Command):
    def _deactive_vte(self, vte):
        print("disabled")
        vte.set_input_enabled(False)
        vte.set_property("can_focus", False)
        vte.set_property("sensitive", False)

    def _child_exit(self, vte, status):
        print("child-exit")
        print(status)

        self._deactive_vte(vte)

    def _resize_container(self, vte):
        # TODO: find proper way to set the height
        new_height = (self.vte.get_cursor_position().row + 2 )*self.vte.get_char_height()
        self.container.set_property("height-request", min(max(new_height, 400), 1000))

    def parse_input(self, raw_input):
        # TODO: find proper way to run quick commands
        escaped = shlex.quote(raw_input + "; sleep 2")

        return ["/usr/bin/bash", "-c", escaped[1:-1]]

    def execute(self, parsed_input):
        print(parsed_input)
        self.vte = Vte.Terminal.new()
        self.vte.connect("eof", self._deactive_vte)
        self.vte.connect("child-exited", self._child_exit)
        self.vte.spawn_sync(Vte.PtyFlags.DEFAULT, self._cwd(), parsed_input, self._env(), GLib.SpawnFlags.SEARCH_PATH_FROM_ENVP, None)
        return self.vte

    def display_output(self, parsed_output):

        self.container = Gtk.VBox()

        self.vte.connect("contents-changed", self._resize_container)
        self.container.pack_start(self.vte, True, True, 0)
        return self.container

commands = {
    "l1commands": {
        "ls": Ls,
        "image": Image,
        "cd": Cd,
        "web": Web
    },
    "default": Bash
}
