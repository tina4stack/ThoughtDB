#
# Tina4 - This is not a 4ramework.
# Copy-right 2007 - current Tina4
# License: MIT https://opensource.org/licenses/MIT
#
from cleantext import clean


class Core:

    def __init__(self, vector_store):
        self.database = vector_store.database
        self.vector_store = vector_store
        self._id = 0
        self.data = {}

    def system_name(self, text, punctuation=True):
        """
        Cleans up weird text inputs
        :param punctuation:
        :param text:
        :return:
        """
        return clean(text, punct=punctuation, stemming=False, lowercase=True)

    def get_basic_dataset(self, name, dataset, data_type, data_name="", filter="id <> 0",
                          additional_data = None,
                          raise_exception=True):
        if dataset == {}:
            result = self.database.fetch(f"select * from {data_name} where {filter}")

            if result is not None:
                dataset = {}
                for record in result.records:
                    dataset[record["name"]] = data_type(self, record["id"], additional_data=additional_data)
                    dataset[record["name"]].data = record

        if name == "":
            return dataset
        else:
            if dataset is not {}:
                if name in dataset:
                    return dataset[name]
                else:
                    if raise_exception:
                        raise Exception(f"No {data_name} with name {name}")
                    else:
                        return  {}
            else:
                if raise_exception:
                    raise Exception(f"No {data_name} with name {name}")
                else:
                    return  {}

    def _load(self, name, id, data_name):
        if id != 0:
            self._id = id
            self.data = self.database.fetch_one(f"select * from {data_name} where id = ?", [self._id])
        else:
            self.data = self.database.fetch_one(f"select * from {data_name} where name = ?", [self.system_name(name)])
            if self.data is not None:
                self._id = self.data["id"]
        return self.data

    def _create(self, name, data_name, additional_data=None):
        create_data = {"name": self.system_name(name)}
        if additional_data is not None:
            create_data.update(additional_data)
        data = self.database.insert(data_name, create_data)
        self.database.commit()
        return data

    def _update(self, name, data_name, id=0):
        if id != 0:
            self._id = id
        self._load(name, id, data_name)
        self.database.update(data_name, {"name": self.system_name(name), "id": id})
        self.database.commit()
        return self

    def _delete(self, name='', id=0, data_name=""):
        if id != 0:
            self._id = id
            self.database.delete(data_name, {"id": self._id})
        else:
            self.database.delete(data_name, {"name": name})
        self.database.commit()
        self._id = 0
        self.data = None
        return self.data