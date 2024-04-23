from enum import Flag

"""renpy
init -1 python:
"""


class LovenseAction(Flag):
    VIBRATE = 1 << 0
    ROTATE = 1 << 1
    PUMP = 1 << 2
    THRUST = 1 << 3
    FINGER = 1 << 4
    SUCTION = 1 << 5
    DEPTH = 1 << 6

    @staticmethod
    def ALL() -> "LovenseAction":
        return (
            LovenseAction.VIBRATE
            | LovenseAction.ROTATE
            | LovenseAction.PUMP
            | LovenseAction.THRUST
            | LovenseAction.FINGER
            | LovenseAction.SUCTION
            | LovenseAction.DEPTH
        )
