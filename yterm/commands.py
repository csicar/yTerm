import argparse
import os
import json
from subprocess import Popen
import subprocess


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk




class Command:
    def parse_input(raw_input):
        pass

    def execute(self, parsed_input):
        pass

    def display_output(self, parsed_output):
        pass

#def table_renderer(data):


class RenderedCommand(Command):
    def display_output(self, parsed_output):
        mime_type = parsed_output['mimeType']
        sub_type = parsed_output['subtype']
        data = parsed_output['data']

class LS(Command):
    def __init__(self):
        self.name = "ls"

    def parse_input(self, raw_input):
        print("parse_input")
        print(raw_input)
        return raw_input.split(" ")

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
            print(entry["type"])
            icon = Gtk.Image(stock=icon_types[entry["type"]])
            entry_view.pack_start(icon, False, False, 0)
            entry_view.pack_start(Gtk.Label(entry["name"]), False, False, 0)
            flow.insert(entry_view, -1)
        return flow


class Bash(Command):
    def __init__(self):
        self.name = "ls"

    def parse_input(self, raw_input):
        return raw_input

    def execute(self, parsed_input):
        output = Popen(parsed_input, shell=True, stdout=subprocess.PIPE).stdout.read()
        return output.decode("utf-8")

    def display_output(self, parsed_output):
        builder = Gtk.Builder()
        builder.add_from_file("process.glade")
        textview = builder.get_object("textview")
        textview.get_buffer().set_text(parsed_output)
        return textview;

commands = {
    "l1commands": {
        "ls": LS
    },
    "default": Bash
}
