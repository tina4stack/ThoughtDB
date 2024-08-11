#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from thoughtdb.app.Core import Core


class Document(Core):

    def __init__(self, vector_store):
        self.id = 0
        super(Document, self).__init__(vector_store)
