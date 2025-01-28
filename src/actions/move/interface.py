from dataclasses import dataclass
from enum import Enum

from actions.base import Interface


class MovementAction(str, Enum):
    STAND_STILL = "stand still"
    SIT = "sit"
    DANCE = "dance"
    SHAKE_PAW = "shake paw"
    WALK = "walk"
    WALK_BACK = "walk back"
    RUN = "run"
    JUMP = "jump"


@dataclass
class MoveInput:
    action: MovementAction


@dataclass
class Move(Interface[MoveInput, MoveInput]):
    """
    A movement to be performed by the agent.

    Effect: Allows the agent to move.
    """

    input: MoveInput
    output: MoveInput
