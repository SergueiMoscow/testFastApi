def cursor_to_dict(cursor: psycopg2.cursor) -> dict:
    result = {}
    fields = [column.name for column in cursor.description]
    for column in cursor.description:
        for row in cursor:


