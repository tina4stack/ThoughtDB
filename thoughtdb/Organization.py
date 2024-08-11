#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from thoughtdb.Collection import Collection
from thoughtdb.Core import Core


class Organization(Core):

    def __init__(self, vector_store, id=0):
        """
        Initialize the Organization
        :param vector_store: 
        """
        self._id = id
        self.data = None
        self._collections = {}
        super(Organization, self).__init__(vector_store)

    def set_collections(self):
        """
        Sets a collection to the correct organization
        :return:
        """
        self._collections = self.get_collections()

    def load(self, name="", id=0):
        """
        Load an organization by its name or id
        :param name:
        :return:
        """
        self._load(name,id, "organization")
        self.set_collections()
        return self

    def create(self, name):
        data = self._create(name, "organization")
        self.load(id=data.records[0]["id"])
        return self

    def update(self, name, id=0):
        self._update(name, "organization", id)
        self.data["name"] = self.system_name(name)
        return self

    def delete(self, name='', id=0):
        self._delete(name, id, "organization")
        return self

    def get_collections(self, name="", raise_exception=True):
        return self.get_basic_dataset(name, self._collections, Collection, "collection",
                                      filter="id <> 0 and organization_id = "+str(self._id),
                                      additional_data={"organization_id": self._id},
                                      raise_exception=raise_exception)

    def get_collection(self, name, create=False):
        collection = self.get_collections(name, False)
        if collection is None and create:
            collection = Collection(self, additional_data={"organization_id": self._id})
            collection.create(name)

        return collection
