#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from thoughtdb.Core import Core
from thoughtdb.Document import Document
from thoughtdb.Conversation import Conversation


class Collection(Core):

    def __init__(self, vector_store, id=0, additional_data=None):
        self._id = id
        self._documents = {}
        self._conversations = {}
        self._organization_id = 0
        if additional_data is not None:
            if "organization_id" in additional_data:
                self._organization_id = additional_data["organization_id"]
        super(Collection, self).__init__(vector_store)

    def set_documents(self):
        """
        Sets documents to the correct collection
        :return:
        """
        self._documents = self.get_documents()

    def set_conversations(self):
        """
        Sets a collection to the correct collection
        :return:
        """
        self._conversations = self.get_conversations()

    def load(self, name="", id=0):
        """
        Load a collection by its name or id
        :param name:
        :return:
        """
        self._load(name, id, "collection")
        self.set_documents()
        self.set_conversations()
        return self

    def create(self, name):
        data = self._create(name, "collection", {"organization_id": self._organization_id})
        self.load(id=data.records[0]["id"])
        return self

    def update(self, name, id=0):
        self._update(name, "collection", id)
        self.data["name"] = self.system_name(name)
        return self

    def delete(self, name='', id=0):
        self._delete(name, id, "collection")
        return self

    def get_documents(self, name="", raise_exception=True):
        return self.get_basic_dataset(name, self._documents, Document, "document",
                                      filter="id <> 0 and organization_id = " + str(
                                          self._organization_id) + " and collection_id = " + str(self._id),
                                      additional_data={"organization_id": self._organization_id},
                                      raise_exception=raise_exception)

    def get_document(self, name, create=False):
        document = self.get_documents(name, False)
        if document is None and create:
            document = Document(self)
            document.create(name)

        return document

    def get_conversations(self, name="", raise_exception=True):
        return self.get_basic_dataset(name, self._conversations, Conversation, "conversation",
                                      filter="id <> 0 and organization_id = " + str(
                                          self._organization_id) + " and collection_id = " + str(self._id),
                                      raise_exception=raise_exception)

    def get_conversation(self, name, create=False):
        conversation = self.get_conversations(name, False)
        if conversation is None and create:
            conversation = Conversation(self)
            conversation.create(name)

        return conversation
