from pony.orm import Database, Required

db = Database()


class Users(db.Entity):
    _table_ = "users"
    tg_id = Required(str, 10)
    name = Required(str)
    lang = Required(str, 3, default="he")
    role = Required(str, 5, index=True, default="user")
    active = Required(bool, default=True)


db.bind(provider="sqlite", filename="get_chat_id.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
