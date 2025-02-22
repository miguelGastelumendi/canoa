# Equipe da Canoa -- 2024
#
#  A helper to keep data between sessions
#     STILL UNDER DEVELOPMENT
#
# mgd 2024-10-17

# cSpell:ignore


import json
from flask import session
from datetime import datetime

from .user_helper import now


class InterSessions:
    def __init__(self, app_mode):
        self.app_mode = "DEBUG"
        self.started = now()
        self.ready = True

    def to_json(self):
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        data["started"] = datetime.fromisoformat(data["started"])
        return cls(**data)


@app.route("/")
def index():
    if "persisted_data" not in session:
        persisted = Persisted()
        session["persisted_data"] = persisted.to_json()
    else:
        persisted_json = session["persisted_data"]
        persisted = Persisted.from_json(persisted_json)
    return f"Persisted data: {persisted.app_mode}, {persisted.started}, {persisted.ready}"


if __name__ == "__main__":
    app.run(debug=True)
