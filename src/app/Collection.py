#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from src.app.Core import Core
from src.app.Document import Document


class Collection(Core):

    def __init__(self, vector_store):
        self.document = Document(vector_store)
        self.id = 0
        super(Collection, self).__init__(vector_store)