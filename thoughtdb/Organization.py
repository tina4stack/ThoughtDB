#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from thoughtdb.Collection import Collection
from thoughtdb.Core import Core
import hashlib


class Organization(Core):

    def __init__(self, vector_store, id=0, additional_data=None):
        """
        Initialize the Organization
        :param vector_store: 
        """
        if additional_data is None:
            additional_data = {}
        self._id = id
        self.data = None
        self._collections = {}
        self.additional_data = additional_data
        super(Organization, self).__init__(vector_store, id=id)


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
        data = self._load(name, id, "organization")
        if data is None:
            raise Exception(f"Error loading organisation {name} {id} ")
        else:
            self.set_collections()
        return self

    def create(self, name):
        self.additional_data={"auth_key": hashlib.md5(name.encode()).hexdigest()}
        data = self._create(name, "organization", self.additional_data)

        if data:
            self.load(id=data.records[0]["id"])
        return self

    def update(self, name, id=0):
        self.additional_data={"auth_key": hashlib.md5(name.encode()).hexdigest()}
        self._update(name, "organization", id, self.additional_data)
        self.data["name"] = self.system_name(name)
        return self

    def delete(self, name='', id=0):
        self._delete(name, id, "organization")
        return self

    def get_collections(self, name="", id=0, raise_exception=True):
        """
        Gets a collection by name or id
        :param name:
        :param id:
        :param raise_exception:
        :return:
        """
        return self.get_basic_dataset(self.system_name(name), self._collections, Collection, "collection",
                                      filter="id <> 0 and organization_id = " + str(self._id),
                                      additional_data={"organization_id": self._id},
                                      id=id,
                                      raise_exception=raise_exception)

    def get_collection(self, name="", id=0, create=False):
        """
        Gets a collection by name or id
        :param name:
        :param id:
        :param create:
        :return:
        """
        collection = self.get_collections(name, id=id, raise_exception=False)
        if collection != {}:
            return collection

        if collection == {} and create:
            collection = Collection(self, additional_data={"organization_id": self._id})
            collection.create(name)
        else:
            if collection == {}:
                raise Exception(f"No collection found: {name} {id}")

        return collection
