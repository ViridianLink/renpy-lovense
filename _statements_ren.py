from typing import Any, Callable, Optional, Sequence

from LovenseAction_ren import LovenseAction
from Lovense_ren import Lovense
from renpy.lexer import Lexer
import renpy.exports as renpy


path_builder: bool
lovense = Lovense()

"""renpy
python early:
"""


def parse_parenthesises(lexer: "Lexer", start: str) -> list[str]:
    rv: str = ""
    if start == "(":
        lexer.pos += 1
        rv = lexer.delimited_python(")", False)  # type: ignore
        lexer.pos += 1
    elif start == "[":
        lexer.pos += 1
        rv = lexer.delimited_python("]", False)  # type: ignore
        lexer.pos += 1
    return rv.split(",")


def parse_lovense(lexer: "Lexer") -> tuple[list[str], list[str]]:
    lexer.skip_whitespace()

    start = lexer.text[lexer.pos]
    actions = list(map(lambda a: a.strip(), parse_parenthesises(lexer, start)))

    if not actions:
        lexer.error("Expected actions.")

    if "stop" in actions:
        return (["stop"], ["0"])

    lexer.skip_whitespace()
    start = lexer.text[lexer.pos]
    strengths = list(map(lambda s: s.strip(), parse_parenthesises(lexer, start)))

    if not strengths:
        lexer.error("Expected strengths.")

    if len(actions) != len(strengths):
        lexer.error("Mismatched number of actions and strengths.")

    return (actions, strengths)


def lint_lovense(expr: tuple[list[str], list[str]]) -> None:
    actions, strengths = expr

    if "stop" in actions:
        return

    for action, strg in zip(actions, strengths):
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

        try:
            strength: Any = eval(strg)
        except (SyntaxError, TypeError) as e:
            renpy.error(
                f"The strength expression '{expr[1]}' could not be evaluated due to an error: {e}"
            )
            return
        except NameError as e:
            strength = 0
            renpy.error(
                f"Warning: Usage of variables cannot be checked at lint time. {e}"
            )

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


def execute_lovense(expr: tuple[list[str], list[str]]) -> None:
    actions, strengths = expr

    if "stop" in actions:
        lovense.stop()
        return

    lovense_action = LovenseAction(0)
    for action in actions:
        lovense_action |= LovenseAction[action.upper()]

    lovense.send_function(lovense_action, map(lambda s: eval(s), strengths))

    return


renpy.register_statement(  # type: ignore
    name="lovense",
    parse=parse_lovense,
    lint=lint_lovense,
    execute=execute_lovense,
)
