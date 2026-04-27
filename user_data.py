from enum import Enum, auto
from dataclasses import dataclass

class State(Enum):
    NONE = auto()
    CHOOSING = auto()
    IMAGE_GEN = auto()
    STATISTICS = auto()
    QUIZ = auto()
    FINISHED = auto()


@dataclass(slots=True)
class UserDataDC:
    user_id: int = 0
    state: State = State.NONE
