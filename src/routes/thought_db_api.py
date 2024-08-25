from tina4_python.Router import get, post, delete, patch
from tina4_python.Swagger import description, tags, example, secure, params
from src import vector_store


@get("/test/{search}")
async def api_test(request, response):
    data = vector_store.database.fetch(
        "select id, table_name, key_name , key_value  from embedding where id in (select value from json_each(search('" +
        request.params["search"] + "', 5)))")

    result = []
    for record in data.records:
        sql = "select * from " + record["table_name"] + " where " + record["key_name"] + " = '" + record[
            "key_value"] + "'"
        result_data = vector_store.database.fetch_one(sql)
        result.append(result_data)

    return response(result)


@post("/api/search")
@description("Search Data")
@params(["key", "collection_id"])
@tags("Search")
@example({"query": "Give me some documents which relate to fish",
          "filter": {"metadata": [["fish", "farm-animals"], ["land"]], "documentType": "All|Text|Image|PDF"},
          "limit": 10})
# ! before the word means not = [['a', 'b'], ['!c']] = a and b or not c
# single list = ['a', 'b'] = a and b
# multi list = [['a', 'b'], ['c']] = a and b or c
@secure()
async def api_get_organizations(request, response):
    pass


@get("/api/organizations")
@description("Get all the organizations")
@tags("Organizations")
@secure()
async def get_api_organisations(request, response):
    try:
        organisations = vector_store.get_organizations("")

        result = []
        for key in organisations:
            result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"],
                           "auth_key": organisations[key].data["auth_key"]})
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@post("/api/organizations")
@description("Create an organization")
@tags("Organizations")
@example({"name": "new_organization"})
@secure()
async def post_api_organizations(request, response):
    try:
        organisation = vector_store.get_organization(request.body["name"], create=True)

        if organisation.data == {}:
            organisation = vector_store.get_organization(request.body["name"])

        result = [{"id": organisation.data["id"], "name": organisation.data["name"],
                   "auth_key": organisation.data["auth_key"]}]
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@get("/api/organizations/{id}")
@description("Get a single organization")
@tags("Organizations")
@secure()
async def get_organizations_id(request, response):
    """
    Gets a single organization
    :param request:
    :param response:
    :return:
    """
    try:
        organisations = vector_store.get_organization("", id=request.params["id"])

        result = []
        for key in organisations:
            collections = []
            collections_result = organisations[key].get_collections()

            for collection_key in collections_result:
                collections.append({"id": collections_result[collection_key].data["id"],
                                    "name": collections_result[collection_key].data["name"]})

            result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"],
                           "auth_key": organisations[key].data["auth_key"], "collections": collections})

    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@delete("/api/organizations/{id}")
@description("Delete a single organization")
@tags("Organizations")
@secure()
async def delete_api_organizations_id(request, response):
    """
    Deletes an organization
    :param request:
    :param response:
    :return:
    """
    result = vector_store.del_organization(id=request.params["id"])

    return response({"error": None})


@get("/api/organizations/{id}/collections")
@description("Get all the collections for an organization")
@tags("Organizations")
@secure()
async def get_api_organizations_id_collections(request, response):
    try:
        organisation = vector_store.get_organization(id=request.params["id"])

        for key in organisation:
            collections = organisation[key].get_collections()

        result = []
        for key in collections:
            result.append({"id": collections[key].data["id"], "name": collections[key].data["name"],
                           "organizationId": collections[key].data["organization_id"]})

    except Exception as e:
        result = {"error": str(e)}
    return response(result)


@post("/api/organizations/{id}/collections")
@description("Add a collections for an organization")
@example({"name": "new_collection"})
@tags("Organizations")
@secure()
async def post_api_organizations_id_collections(request, response):
    try:
        organisation = vector_store.get_organization(id=request.params["id"])
        result = {}

        for key in organisation:
            collection = organisation[key].get_collection(name=request.body["name"], create=True)

            if collection.data == {}:
                collection = organisation[key].get_collection(request.body["name"])

            result = [{"id": collection.data["id"], "name": collection.data["name"],
                       "organizationId": collection.data["organization_id"]}]
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@get("/api/organizations/{id}/collections/{collection_id}")
@description("Get a single collection based on id")
@tags("Organizations")
@secure()
async def get_api_organizations_id_collections_collection_id(request, response):
    """
    Gets a single organization
    :param request:
    :param response:
    :return:
    """
    try:
        organisation = vector_store.get_organization(id=request.params["id"])
        result = {}

        for key in organisation:
            collection = organisation[key].get_collection(id=request.params["collection_id"])
            for collection_key in collection:
                documents = []

                result = [{"id": collection[collection_key].data["id"], "name": collection[collection_key].data["name"],
                           "documents": documents,
                           "organizationId": collection[collection_key].data["organization_id"]}]
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@delete("/api/organizations/{id}/collections/{collection_id}")
@description("Delete a collection from an organization")
@tags("Organizations")
@secure()
async def api_get_organizations_collections_id(request, response):
    organisation = vector_store.get_organization(id=request.params["id"])
    for key in organisation:
        collection = organisation[key].get_collection(id=request.params["collection_id"])
        for collection_key in collection:
            collection[collection_key].delete(collection[collection_key].data["name"])

    return response({"error": None})


@get("/api/collections")
@description("Get all the collections")
@params(["auth_key"])
@tags("Collections")
@secure()
async def api_get_collections(request, response):
    if not "auth_key" in request.params or request.params["auth_key"] == "":
        return response({"error": "Auth key is missing"})
    organisation = vector_store.get_organization(auth_key=request.params["auth_key"])

    print('{"hello": "world"}')




@post("/api/collections")
@description("Add a collection")
@params(["auth_key"])
@tags("Collections")
@secure()
async def api_get_organizations(request, response):
    pass


@delete("/api/collections/{id}")
@description("Delete a collection based on its id")
@params(["key"])
@tags("Collections")
@secure()
async def api_get_organizations(request, response):
    pass


@get("/api/documents")
@description("Get all the collections")
@params(["key", "collection_id"])
@tags("Documents")
@secure()
async def api_get_collections(request, response):
    pass


@get("/api/documents/{id}")
@description("Get a document based on its id")
@params(["key"])
@tags("Documents")
@secure()
async def api_get_organizations(request, response):
    pass


@post("/api/documents")
@description("Add a collection")
@params(["key", "collection_id"])
@tags("Documents")
@secure()
async def api_get_organizations(request, response):
    pass


@patch("/api/documents")
@description("Add a collection")
@params(["key", "collection_id"])
@tags("Documents")
@secure()
async def api_get_organizations(request, response):
    pass


@delete("/api/documents/{id}")
@description("Delete a collection based on its id")
@params(["key"])
@tags("Documents")
@secure()
async def api_get_organizations(request, response):
    pass


@get("/api/conversations")
@description("Get all the collections")
@params(["key", "collection_id"])
@tags("Conversations")
@secure()
async def api_get_collections(request, response):
    pass


@get("/api/conversations/{id}")
@description("Get all the collections")
@params(["key"])
@tags("Conversations")
@secure()
async def api_get_collections(request, response):
    pass


@post("/api/conversations")
@description("Add a collection")
@params(["key", "collection_id"])
@tags("Conversations")
@secure()
async def api_get_organizations(request, response):
    pass


@patch("/api/conversations")
@description("Add a collection")
@params(["key", "collection_id"])
@tags("Conversations")
@secure()
async def api_get_organizations(request, response):
    pass


@delete("/api/conversations/{id}")
@description("Delete a collection based on its id")
@params(["key"])
@tags("Conversations")
@secure()
async def api_get_organizations(request, response):
    pass


@get("/api/images")
@description("Get all the collections")
@params(["key", "collection_id"])
@tags("Images")
@secure()
async def api_get_collections(request, response):
    pass


@get("/api/images/{id}")
@description("Get all the collections")
@params(["key", "collection_id"])
@tags("Images")
@secure()
async def api_get_collections(request, response):
    pass


@post("/api/images")
@description("Add a collection")
@params(["key", "collection_id"])
@tags("Images")
@secure()
async def api_get_organizations(request, response):
    pass


@delete("/api/images/{id}")
@description("Delete a collection based on its id")
@params(["key"])
@tags("Images")
@secure()
async def api_get_organizations(request, response):
    pass
