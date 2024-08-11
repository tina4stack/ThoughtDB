#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from src.app.Collection import Collection
from src.app.Core import Core


class Organization(Core):

    def __init__(self, vector_store):
        """
        Initialize the Organization
        :param vector_store: 
        """
        self.collection = Collection(vector_store)
        self.id = 0
        self.data = None
        super(Organization, self).__init__(vector_store)

    def load(self, name="", id=0):
        """
        Load an organization by its name or id
        :param name:
        :return:
        """
        if id != 0:
            self.id = id
            self.data = self.dba.fetch_one("select * from organization where id = ?", [id])
        else:
            self.data = self.dba.fetch_one("select * from organization where name = ?", [self.system_name(name)])
            self.id = self.data["id"]
        return self

    def create(self, name):
        data = self.dba.insert("organization", {"name": self.system_name(name)})
        self.dba.commit()
        self.load(id=data.records[0]["id"])
        return self

    def update(self, name, id=0):
        if id != 0:
            self.id = id
        self.load(name, id)
        self.dba.update("organization", {"name": self.system_name(name), "id": self.id})
        self.dba.commit()
        self.load(name, id)
        return self

    def delete(self, name='', id=0):
        if id != 0:
            self.id = id
            result = self.dba.delete("organization", {"id": id})
        else:
            result = self.dba.delete("organization", {"name": name})
        print(result)
        self.dba.commit()
        self.id = 0
        self.data = None
        return self
