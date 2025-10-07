from blib.encoding.unicode_encoder import UnicodeEncoder
from blib.formatting.formatter import Formatter


class DoiFormatter(Formatter):

    def format(self, data):
        return data['doi']

