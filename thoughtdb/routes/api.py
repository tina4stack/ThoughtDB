from tina4_python.Router import get, post, delete
from tina4_python.Swagger import description, tags, example, secure
from src import vector_store


@get("/test/{search}")
async def api_test(request, response):
    results = vector_store.database.fetch(
        "select id, embed('document', 'data', 'id', d.id, d.data) as embed from document d", limit=100)

    print(results)

    data = vector_store.database.fetch(
        "select id, table_name, key_name, key_value  from embedding where id in (select value from json_each(search('" +
        request.params["search"] + "', 5)))")

    result = []
    for record in data.records:
        sql = "select * from " + record["table_name"] + " where " + record["key_name"] + " = '" + record[
            "key_value"] + "'"
        result_data = vector_store.database.fetch_one(sql)
        result.append(result_data)

    return response(result)


@get("/api/organizations")
@description("Get all the organizations")
@tags("Organizations")
@secure()
async def api_get_organisations(request, response):
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
    result = vector_store.del_organization(id=request.params["id"])

    return response({"error": None})
