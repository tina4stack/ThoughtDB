import os
from tina4_python.Router import get
from thoughtdb.VectorStore import VectorStore

vector_store = VectorStore("sqlite3:"+os.getenv("DATABASE"))

@get("/test/{search}")
async def api_test(request, response):
    global vector_store

    data = vector_store.database.fetch("select id, table_name, key_name, key_value  from embedding where id in (select value from json_each(search('"+request.params["search"]+"', 5)))")

    print(data)
    result = []
    for record in data.records:
        sql = "select * from "+record["table_name"]+" where "+record["key_name"]+" = '"+record["key_value"]+"'"
        print(sql)
        result_data = vector_store.database.fetch_one(sql)
        result.append(result_data)

    return response(result)

