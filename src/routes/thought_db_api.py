import os
from tina4_python.Router import get, post, delete
from tina4_python.Swagger import description, tags, example, secure
from thoughtdb.VectorStore import VectorStore

vector_store = VectorStore("sqlite3:" + os.getenv("DATABASE"))


@get("/test/{search}")
async def api_test(request, response):
    global vector_store

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
async def api_get_organisations(request, response):
    global vector_store

    organisations = vector_store.get_organizations("")

    result = []
    for key in organisations:
        result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"]})

    return response(result)


@post("/api/organizations")
@description("Create an organization")
@tags("Organizations")
@example({"name": "new_organization"})
@secure()
async def api_post_organisations(request, response):
    global vector_store

    organisation = vector_store.get_organization(request.body["name"], create=True)

    if organisation.data == {}:
        organisation = vector_store.get_organization(request.body["name"])

    result = [{"id": organisation.data["id"], "name": organisation.data["name"]}]
    return response(result)


@get("/api/organizations/{id}")
@description("Get a single organization")
@tags("Organizations")
@secure()
async def api_get_organisations(request, response):
    global vector_store

    organisations = vector_store.get_organization("", id=request.params["id"])

    result = []
    for key in organisations:
        result.append({"id": organisations[key].data["id"], "name": organisations[key].data["name"]})

    return response(result)


@delete("/api/organizations/{id}")
@description("Delete a single organization")
@tags("Organizations")
@secure()
async def api_delete_organisations(request, response):
    global vector_store
    result = vector_store.del_organization(id=request.params["id"])

    return response({"error": None})
