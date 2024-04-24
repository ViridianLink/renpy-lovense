# import datetime
# import json
# import os

from typing import Any
import socketio

# from renpy import config, store
# from renpy.game import persistent
import renpy.exports as renpy

# from game.lovense.LovenseAction_ren import LovenseAction

"""renpy
init python:
"""


class LovenseSocket:
    def __init__(self) -> None:
        self.socket = socketio.Client()

    def get_token(self) -> str:
        return ""

    def validate_authorization(self, auth_token: str) -> dict[str, str]:
        return renpy.fetch(
            "https://api.lovense-api.com/api/basicApi/getSocketUrl",
            method="POST",
            json={"platform": "CrimsonSky", "authToken": str},
        )

    def connect(self, url: str) -> None:
        self.socket.connect(url)  # type: ignore

    def get_qr_code(self, auth_token: str) -> str:
        @socket.event
        def basicapi_get_qrcode_tc(  # pyright: ignore[reportUnusedFunction]
            data: Any,
        ) -> None:
            print(data)

        socket.emit("basicapi_get_qrcode_ts", {"ackId": auth_token})

        return ""
