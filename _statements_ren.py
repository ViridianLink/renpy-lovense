from typing import Any, Callable, Optional

from LovenseAction_ren import LovenseAction
from Lovense_ren import Lovense
from renpy.lexer import Lexer
import renpy.exports as renpy


path_builder: bool
lovense = Lovense()

"""renpy
python early:
"""


def parse_lovense(lexer: "Lexer") -> tuple[str, str]:
    action: Optional[str] = lexer.name()

    if not action:
        lexer.error("Expected action name.")

    if action == "stop":
        return (action, "0")

    strength = lexer.simple_expression()

    if not strength:
        lexer.error("Expected strength.")

    return (action, strength)


def lint_lovense(lovense_expr: tuple[str, str]) -> None:
    action: str = lovense_expr[0]

    try:
        action_func: Any = getattr(lovense, action)
    except AttributeError:
        renpy.error(
            f"Unrecognized lovense action '{action}'. Please check if the action name is correct and supported."
        )
        return

    if not callable(action_func):
        renpy.error(
            f"The lovense action '{action}' is not a function. Please ensure that it is a valid callable action."
        )

    if action == "stop":
        return

    try:
        strength: Any = eval(lovense_expr[1])
    except (SyntaxError, TypeError) as e:
        renpy.error(
            f"The strength expression '{lovense_expr[1]}' could not be evaluated due to an error: {e}"
        )
        return
    except NameError as e:
        strength = 0
        renpy.error(f"Warning: Usage of variables cannot be checked at lint time. {e}")

    if not isinstance(strength, int):
        renpy.error(
            f"The lovense strength value '{strength}' is not an integer. Strength values must be integer types."
        )

    if strength < 0:
        renpy.error(
            f"The lovense strength value '{strength}' is negative. Strength values must be non-negative integers."
        )

    try:
        max_strength: int = Lovense.MAX_STRENGTHS[LovenseAction[action.upper()]]
    except KeyError:
        renpy.error(
            f"The action '{action}' is not associated with a maximum strength value in 'Lovense.MAX_STRENGTHS'."
        )
        return

    if strength > max_strength:
        renpy.error(
            f"The strength '{strength}' exceeds the maximum allowed strength of '{max_strength}' for the action '{action}'."
        )


def execute_lovense(lovense_expr: tuple[str, str]) -> None:
    action: str = lovense_expr[0]
    strength: int = eval(lovense_expr[1])

    f: Callable[..., None] = getattr(lovense, action)

    if action == "stop":
        f()
    else:
        f(strength)

    return


renpy.register_statement(  # type: ignore
    name="lovense",
    parse=parse_lovense,
    lint=lint_lovense,
    execute=execute_lovense,
)
