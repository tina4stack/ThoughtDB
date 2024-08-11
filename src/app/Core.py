#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from cleantext import clean


class Core:

    def __init__(self, vector_store):
        self.dba = vector_store.dba

    def system_name(self, text, punctuation=True):
        """
        Cleans up weird text inputs
        :param punctuation:
        :param text:
        :return:
        """
        return clean(text, punct=punctuation, stemming=False, lowercase=True)

