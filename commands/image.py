from command import Command, parse_fileinput


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class Image(Command):
    def parse_input(self, file):
        return {
            "file": parse_fileinput(self._cwd(), file)
        }

    def execute(self, file):
        return file

    def display_output(self, file):
        return Gtk.Image.new_from_file(file['file'])

def get_command():
    return Image
