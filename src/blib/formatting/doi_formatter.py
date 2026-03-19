from blib.encoding.unicode_encoder import UnicodeEncoder
from blib.formatting.formatter import Formatter


class DoiFormatter(Formatter):

    def format(self, data):
        if 'doi' in data:
            return data['doi']
        if 'eprint' in data and 'archiveprefix' in data:
            return f"{data['archiveprefix']}:{data['eprint']}"

