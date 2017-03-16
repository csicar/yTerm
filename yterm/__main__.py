# __main__.py
#
# Copyright (C) 2017 Carsten Csiky (csicar)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import signal
import gi
import subprocess
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from subprocess import Popen


class ProcessHistory:
    def __init__(self, view):
        self.view = view;

    def add_history_element(self, element):
        self.view.pack_start(element, True, True, 0)
        self.view.show_all()


class Handler:
    def __init__(self, process_history):
        self.process_history = process_history;

    def runCommand(self, entry):
        raw_command = entry.get_buffer().get_text()
        output = Popen(raw_command, shell=True, stdout=subprocess.PIPE).stdout.read()
        builder = Gtk.Builder()
        builder.add_from_file("application.glade")
        textview = builder.get_object("process_textview")
        textview.get_buffer().set_text(output.decode("utf-8"))
        self.process_history.add_history_element(textview);


class Application(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='org.gnome.Yterm',
                         **kwargs)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("application.glade")
        self.process_history_view = self.builder.get_object("process_history")
        self.process_history = ProcessHistory(self.process_history_view)
        self.builder.connect_signals(Handler(self.process_history))

    def do_activate(self):
        window = Gtk.ApplicationWindow.new(self)
        container = self.builder.get_object("yterm_container")

        window.add(container)
        window.set_default_size(200, 200)
        window.set_title('yterm')
        window.connect("delete-event", Gtk.main_quit)
        window.show_all()


def main():
    application = Application()

    try:
        ret = application.run(sys.argv)
    except SystemExit as e:
        ret = e.code

    sys.exit(ret)


if __name__ == '__main__':
    main()
