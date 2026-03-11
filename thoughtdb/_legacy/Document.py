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
        super(Document, self).__init__(vector_store, id=id)

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
            self.data["metadata"] = metadata

            

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

    def parse_document_text(self, text):
        lines = text.split("\n")
        paragraphs = []
        paragraph = ""
        for line in lines:
            paragraph += line
            if line.strip() == "":
                paragraphs.append(segment)
                segment = ""
        sentences = []
        for paragraph in paragraphs:
            sentence_list = paragraph.replace('\n', " ").strip().split(".")
            for sentence in sentence_list:
                if sentence != "":
                    sentences.append(sentence)

        return paragraphs, sentences
