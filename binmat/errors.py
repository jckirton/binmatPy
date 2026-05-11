class InvalidOp(Exception):
    """An invalid BINMAT op."""


class DrainedDeck(Exception):
    """The deck is completely drained."""


class GameEnd(Exception):
    """The game has ended."""


class DefenderWin(GameEnd):
    """The defender win condition is met."""


class AttackerWin(GameEnd):
    """The attacker win condition is met."""
