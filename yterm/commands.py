import argparse
import os
import json
from subprocess import Popen
import subprocess
import shlex
from command import Command, parse_fileinput


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, WebKit, Vte, GLib, GObject


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
        self.container.set_property("height-request", min(max(new_height, 200), 1000))

    def parse_input(self, raw_input):
        # sleep 2 is necessary for quickly terminating commands like "cat"
        # to display any output to the vte.
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
        "cd": Cd,
    },
    "default": Bash
}
