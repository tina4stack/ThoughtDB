#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from logging import raiseExceptions

from thoughtdb.Core import Core


class Document(Core):

    def __init__(self, vector_store, id=0, additional_data=None):
        self._id = id
        self._organization_id = 0
        self._collection_id = 0
        if additional_data is not None:
            if "organization_id" in additional_data:
                self._organization_id = additional_data["organization_id"]
            if "collection_id" in additional_data:
                self._collection_id = additional_data["collection_id"]
        super(Document, self).__init__(vector_store)

    def load(self, name="", id=0):
        """
        Load a collection by its name or id
        :param name:
        :return:
        """
        self._load(name, id, "document")

    def create(self, name, document_type_id=1):
        data = self._create(name, "document", {"document_type_id": document_type_id, "collection_id": self._collection_id, "organization_id": self._organization_id})
        self.load(id=data.records[0]["id"])
        return self

    def update(self, id = 0, name="", data={}, metadata={}):
        if id != 0:
            self._id = id
            self.load(name, id)
        if name != "":
            self.load(name)

        if self.data is not None:
            self.data["data"] = data
            # set metadata
            self.database.update("document", self.data)
            self.database.commit()
        else:
            raise Exception(f"Document not found {name} {id}")

    def append(self, id = 0, name="", data={}, metadata={}):
        if id != 0:
            self._id = id
            self.load(name, id)
        if name != "":
            self.load(name)

        if self.data is not None:
            self.data["data"] += data
            # merge and append metadata
            self.database.update("document", self.data)
            self.database.commit()
        else:
            raise Exception(f"Document not found {name} {id}")
