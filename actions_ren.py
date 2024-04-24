from typing import Any

from Lovense_ren import lovense

from renpy.ui import Action
import renpy.exports as renpy

"""renpy
init python:
"""


class LovenseRefresh(Action):
    def __call__(self) -> Any:
        renpy.restart_interaction()
        return lovense.refresh()


class LovenseQRCodeDownload(Action):
    def __call__(self) -> Any:
        renpy.restart_interaction()
        return lovense.download_qr_code()
