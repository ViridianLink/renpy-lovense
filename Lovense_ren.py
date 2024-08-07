import datetime
import json
import os
from typing import Any, ClassVar, Iterable, Optional, Sequence, Union

from renpy import config, store
from renpy.game import persistent
import renpy.exports as renpy

from LovenseAction_ren import LovenseAction

SERVER_URL: str = ""
QR_CODE_ENDPOINT: str = ""
USERS_ENDPOINT: str = ""

"""renpy
init 1 python:
"""


class Lovense:
    MAX_STRENGTHS: ClassVar[dict[LovenseAction, int]] = {
        LovenseAction.VIBRATE: 20,
        LovenseAction.ROTATE: 20,
        LovenseAction.PUMP: 3,
        LovenseAction.THRUST: 20,
        LovenseAction.FINGER: 20,
        LovenseAction.SUCTION: 20,
        LovenseAction.DEPTH: 3,
    }

    server_online: bool = True

    def __init__(self) -> None:
        self.local_ip: str = ""
        self.http_port: str = ""

        self.last_refresh: datetime.datetime = datetime.datetime.now()

        self.status_message: str = ""
        self.toys: dict[str, str] = {}
        self.last_updated: datetime.datetime = datetime.datetime.min

        self.current_strengths: dict[LovenseAction, int] = {
            action: 0 for action in LovenseAction
        }

    def server_status(self) -> None:
        try:
            renpy.fetch(SERVER_URL, timeout=3)
        except Exception as e:
            print(e)
            self.status_message = "Server Offline. Please connect with Game Mode"
            self.server_online = False
            return

        self.status_message = ""
        self.server_online = True

    @staticmethod
    def _strengths(
        s: Union[Iterable[int], int, float], actions: LovenseAction
    ) -> tuple[int, ...]:
        if isinstance(s, Iterable):
            return tuple(s)

        if isinstance(s, int):
            return (s,)

        # if isinstance(s, float):
        return tuple(
            round(Lovense.MAX_STRENGTHS[action] * s)
            for action in LovenseAction
            if action in actions
        )

    def _send_json_request(
        self,
        url: str = SERVER_URL,
        endpoint: str = "",
        json: Any = None,
    ):
        if url == SERVER_URL and not self.server_online:
            return

        try:
            result = renpy.fetch(
                f"{url}/{endpoint}",
                method="POST",
                json=json,
                result="json",
            )

            return result
        except Exception as e:
            print(e)

    def _send_command(self, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        return self._send_json_request(
            f"http://{self.local_ip}:{self.http_port}", "command", data
        )

    def send_function(
        self,
        actions: LovenseAction,
        strengths: Union[Iterable[int], float],
        time_sec: float = 0,
        stop_previous: bool = True,
    ) -> None:
        strengths = self._strengths(strengths, actions)
        filtered_actions = tuple(
            action for action in LovenseAction if action in actions
        )
        actions_with_strengths = zip(filtered_actions, strengths)

        data: dict[str, object] = {
            "command": "Function",
            "action": ",".join(
                f"{action.name.capitalize()}:{strength}"
                for action, strength in actions_with_strengths
            ),
            "timeSec": time_sec,
            "stopPrevious": int(stop_previous),
            "apiVer": 1,
        }

        if self._send_command(data) is not None:
            for action, strength in actions_with_strengths:
                self.current_strengths[action] = strength

    def get_toys(self) -> None:
        data: dict[str, str] = {"command": "GetToys"}

        result = self._send_command(data)
        if result is None:
            return

        try:
            self.toys = json.loads(result["data"]["toys"])
        except Exception:
            self.toys = {}

    def vibrate(
        self,
        strength: Union[Sequence[int], int, float],
        time: float = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.VIBRATE)
        self.send_function(LovenseAction.VIBRATE, strength, time, stop_previous)

    def rotate(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.ROTATE)
        self.send_function(LovenseAction.ROTATE, strength, time, stop_previous)

    def pump(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.PUMP)
        self.send_function(LovenseAction.PUMP, strength, time, stop_previous)

    def thrust(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.THRUST)
        self.send_function(LovenseAction.THRUST, strength, time, stop_previous)

    def finger(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.FINGER)
        self.send_function(LovenseAction.FINGER, strength, time, stop_previous)

    def suction(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.SUCTION)
        self.send_function(LovenseAction.SUCTION, strength, time, stop_previous)

    def depth(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        strength = self._strengths(strength, LovenseAction.DEPTH)
        self.send_function(LovenseAction.DEPTH, strength, time, stop_previous)

    def all(
        self,
        strength: Union[Sequence[int], int, float],
        time: int = 0,
        stop_previous: bool = True,
    ) -> None:
        actions = LovenseAction.ALL()
        strength = self._strengths(strength, actions)
        self.send_function(actions, strength, time, stop_previous)

    def stop(self) -> None:
        data: dict[str, Any] = {
            "command": "Function",
            "action": "Stop",
            "timeSec": 0,
            "apiVer": 1,
        }

        self._send_command(data)

        self.current_strengths = {s: 0 for s in self.current_strengths}

    def download_qr_code(self) -> None:
        try:
            endpoint = QR_CODE_ENDPOINT
        except NameError:
            endpoint = "api/v1/lovense/qr_code"

        result = self._send_json_request(
            endpoint=endpoint,
            json={"uid": str(persistent.uuid), "uname": store.name},
        )

        if result is not None:
            with open(os.path.join(config.gamedir, "lovense_qr_code.jpg"), "wb") as f:
                f.write(renpy.fetch(result["data"]["qr"]))

    def set_user(self) -> None:
        if not self.server_online:
            return

        try:
            endpoint = USERS_ENDPOINT
        except NameError:
            endpoint = "api/v1/lovense/users"

        try:
            lovense_user = renpy.fetch(
                f"{SERVER_URL}/{endpoint}/{persistent.uuid}", result="json"
            )
        except Exception as e:
            print(e)
            self.status_message = "User not found."
            return

        self.http_port = lovense_user["http_port"]
        self.local_ip = lovense_user["domain"]
        self.last_updated = datetime.datetime.fromisoformat(lovense_user["last_update"])

    def refresh(self) -> None:
        self.download_qr_code()
        self.set_user()
        if self.local_ip and self.http_port:
            self.get_toys()
        self.last_refresh = datetime.datetime.now()


lovense = Lovense()
