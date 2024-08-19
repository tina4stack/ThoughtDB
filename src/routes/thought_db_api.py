from tina4_python.Router import get, post, delete
from tina4_python.Swagger import description, tags, example, secure
from src import vector_store


@get("/test/{search}")
async def api_test(request, response):
    data = vector_store.database.fetch(
        "select id, table_name, key_name, key_value  from embedding where id in (select value from json_each(search('" +
        request.params["search"] + "', 5)))")

    result = []
    for record in data.records:
        sql = "select * from " + record["table_name"] + " where " + record["key_name"] + " = '" + record[
            "key_value"] + "'"
        print(sql)
        result_data = vector_store.database.fetch_one(sql)
        result.append(result_data)

    return response(result)


@get("/api/organizations")
@description("Get all the organizations")
@tags("Organizations")
@secure()
async def api_get_organizations(request, response):
    try:
        organisations = vector_store.get_organizations("")

        result = []
        for key in organisations:
            result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"]})
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@post("/api/organizations")
@description("Create an organization")
@tags("Organizations")
@example({"name": "new_organization"})
@secure()
async def api_post_organizations(request, response):
    try:
        organisation = vector_store.get_organization(request.body["name"], create=True)

        if organisation.data == {}:
            organisation = vector_store.get_organization(request.body["name"])

        result = [{"id": organisation.data["id"], "name": organisation.data["name"]}]
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@get("/api/organizations/{id}")
@description("Get a single organization")
@tags("Organizations")
@secure()
async def api_get_organizations(request, response):
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
            result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"]})
    except Exception as e:
        result = {"error": str(e)}

    return response(result)


@delete("/api/organizations/{id}")
@description("Delete a single organization")
@tags("Organizations")
@secure()
async def api_delete_organizations(request, response):
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
@tags("Collections")
@secure()
async def api_get_organizations_collections(request, response):
    try:
        organisation = vector_store.get_organization(id=request.params["id"])

        for key in organisation:
            collections = organisation[key].get_collections()

        result = []
        for key in collections:
            result.append({"id": collections[key].data["id"], "name": collections[key].data["name"]})

    except Exception as e:
        result = {"error": str(e)}
    return response(result)


@post("/api/organizations/{id}/collections")
@description("Add a collections for an organization")
@example({"name": "new_collection"})
@tags("Collections")
@secure()
async def api_get_organizations_collections(request, response):
    try:
        organisation = vector_store.get_organization(id=request.params["id"])
        result = {}

        for key in organisation:
            collection = organisation[key].get_collection(name=request.body["name"], create=True)

            if collection.data == {}:
                collection = organisation[key].get_collection(request.body["name"])

            result = [{"id": collection.data["id"], "name": collection.data["name"], "organizationId": collection.data["organization_id"]}]
    except Exception as e:
        result = {"error": str(e)}

    return response(result)
