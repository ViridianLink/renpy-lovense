import datetime
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
init python:
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

    def __init__(self) -> None:
        self.local_ip: str = ""
        self.http_port: str = ""

        self.last_refresh: datetime.datetime = datetime.datetime.now()

        self.server_online: bool = False
        self.status_message: str = ""
        self.toys: dict[str, str] = {}
        self.last_updated: int = 0

        self.current_strengths: dict[LovenseAction, int] = {
            action: 0 for action in LovenseAction
        }

    @staticmethod
    def _strengths(
        s: Union[Iterable[int], int, float], actions: LovenseAction
    ) -> tuple[int, ...]:
        if isinstance(s, Iterable):
            return tuple(s)

        if isinstance(s, int):
            return (s,)

        # if isinstance(s, float):
        return tuple(round(Lovense.MAX_STRENGTHS[action] * s) for action in actions)

    def _send_json_request(
        self,
        url: str = SERVER_URL,
        endpoint: str = "",
        json: Any = None,
    ):
        if not self.get_server_status():
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
            if config.developer:
                raise
            print(e)
            self.server_online = False

    def _send_command(self, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        return self._send_json_request(
            f"http://{self.local_ip}:{self.http_port}", "/command", data
        )

    def send_function(
        self,
        actions: LovenseAction,
        strengths: Union[Iterable[int], float],
        time_sec: float = 0,
        stop_previous: bool = True,
    ) -> None:
        strengths = self._strengths(strengths, actions)
        actions_with_strengths = zip(actions, strengths)

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

        self.toys = result["data"]["toys"]

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

    def get_server_status(self) -> bool:
        try:
            renpy.fetch(SERVER_URL, timeout=3)
        except Exception as e:
            print(e)
            self.server_online = False
            self.status_message = "Server Offline. Please connect with Game Mode"
            return False

        self.status_message = ""
        return True

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
        if not self.get_server_status():
            return

        try:
            endpoint = USERS_ENDPOINT
        except NameError:
            endpoint = "api/v1/lovense/users"

        try:
            lovense_user = renpy.fetch(f"{SERVER_URL}/{endpoint}/{persistent.uuid}")
        except Exception as e:
            self.status_message = "User not found."
            print(e)
            return

        self.http_port = lovense_user["http_port"]
        self.local_ip = lovense_user["domain"]
        self.last_updated = lovense_user["last_update"]

    def refresh(self) -> None:
        self.download_qr_code()
        self.set_user()
        self.get_toys()
        self.last_refresh = datetime.datetime.now()


lovense = Lovense()
