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
import os
import getpass
import subprocess

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import commands

settings = Gtk.Settings.get_default()
settings.set_property("gtk-application-prefer-dark-theme", True)
context = {
    "cwd": os.getcwd(),
    "env": [],
}
history = []

class ProcessHistory:
    def __init__(self, view):
        self.view = view;

    def add_history_element(self, element, command):
        builder = Gtk.Builder()
        builder.add_from_file("application.glade")
        item = builder.get_object("process_history_item")
        content = builder.get_object("process_history_content")
        scroll_pane = builder.get_object("process_history_scroll")
        content.pack_start(element, True, True, 0)
        name = builder.get_object("process_history_name")
        user = builder.get_object("process_history_user")
        cwd = builder.get_object("process_history_cwd")
        name.set_text(command)
        user.set_text(getpass.getuser())
        cwd.set_text(context['cwd'])
        self.view.insert(item,-1)
        scroll_pane.do_scroll_child(scroll_pane, Gtk.ScrollType.END, True)
        self.view.show_all()
        #TODO: make it scroll to the bottom


class Handler:
    def __init__(self, process_history):
        self.process_history = process_history;

    def runCommand(self, entry):
        raw_command = entry.get_buffer().get_text()
        splitted = raw_command.split(" ")
        start = splitted[0]
        arguments = raw_command[len(start)+1:]
        view = None
        if start in commands.commands['l1commands'] :
            process = commands.commands['l1commands'][start](context)
            view = process.display_output(process.execute(process.parse_input(arguments)))
        else:
            process = commands.commands['default'](context)
            view = process.display_output(process.execute(process.parse_input(raw_command)))
        self.process_history.add_history_element(view, raw_command);
        entry.grab_focus()

    def commandKeyPress(self, entry, ev, data=None):
        print(ev.keyval)

    def commandPipe(self, entry):
        print(ev.keyval)

class Application(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='org.gnome.Yterm',
                         **kwargs)

        self.builder = Gtk.Builder()
        self.builder.add_from_file("application.glade")
        self.process_history_view = self.builder.get_object("process_history_list")
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
