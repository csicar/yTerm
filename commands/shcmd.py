import argparse
import os
import json
from subprocess import Popen
import subprocess
import shlex
from command import Command


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, WebKit, Vte, GLib, GObject


class ShCmd(Command):

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

def get_command():
    return ShCmd
