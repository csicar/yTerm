import os

def parse_fileinput(cwd, string):
    return os.path.join(cwd, string)

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


class RenderedCommand(Command):
    def display_output(self, parsed_output):
        mime_type = parsed_output['mimeType']
        sub_type = parsed_output['subtype']
        data = parsed_output['data']
