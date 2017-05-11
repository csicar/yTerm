import os
from command import Command, parse_fileinput


import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit', '3.0')
from gi.repository import Gtk, WebKit, GLib, GObject

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

def get_command():
    return Web
