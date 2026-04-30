from random import shuffle
from copy import deepcopy
from typing import Literal

from constants import AXIOMS, CARD_VALUES, TEAMS
from errors import InvalidOp


class Card:
    """A BINMAT card.

    Contains all information about card state.

    Attributes:
        axiom (str): The card's suit, typically one of "%", "&", "+", "!", "^", "#".
        value (str): The value of the card, in symbol form ("@" and not "TRAP", etc.).
        hidden (bool): If the card is hidden. Card is visible to all parties when False.
        face_up (bool): If the card is face-up. Face-up cards are always visible.
        team (int | None): If the card is in the posession of a team. Posessing teams are able to see hidden cards.
    """

    def __init__(
        self,
        axiom: str,
        value: str,
        hidden: bool = False,
        face_up: bool = False,
        team: int | None = None,
    ) -> None:
        """Create a BINMAT Card.

        Args:
            axiom (str): The card's suit.
            value (str): The value of the card, in symbol form.
            hidden (bool, optional): If the card is hidden. Defaults to False.
            face_up (bool, optional): If the card is face-up. Defaults to False.
            team (int | None, optional): If the card is in the posession of a team. Defaults to None.
        """

        self.axiom = axiom
        self.value = value
        self.hidden = hidden
        self.face_up = face_up
        self.team = team

    def __repr__(self):
        if self.hidden:
            return f"{self.value}{self.axiom}x"
        elif self.face_up:
            return f"{self.value}{self.axiom}u"
        else:
            return f"{self.value}{self.axiom}"

    def display(self, team: int | None = None) -> str:
        """Return the card as displayed to the given team.

        Args:
            team (int | None, optional): The "viewing" team, as defined in constants.TEAMS. Defaults to None.
        """

        if self.face_up:
            return f"{self.value}{self.axiom}u"

        if self.team == team or not self.hidden:
            return f"{self.value}{self.axiom}"
        else:
            return "X"

    def __eq__(self, value: object) -> bool:
        if type(value) is str:
            return value in f"{self.value}{self.axiom}"
        # elif type(value) is Card:
        #     return self.axiom == value.axiom and self.value == value.value
        else:
            return self is value


class Discard:
    """A BINMAT discard.

    Contains a collection of Card objects, with methods for adding to and displaying contents.

    Attributes:
        contents (list[Card]): The collection of BINMAT cards in the discard.
        attacker (bool): If the discard is an attacker discard. This changes if the card is set to be face-up.
    """

    def __init__(
        self, attacker: bool = False, contents: list[Card] = [].copy()
    ) -> None:
        """Create a BINMAT discard.

        Args:
            attacker (bool, optional): If the discard is an attacker discard. Defaults to False.
            contents (list[Card], optional): Discard contents. Defaults to [].copy().
        """

        self.contents: list[Card] = contents
        self.attacker: bool = attacker

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)

    def __repr__(self) -> str:
        return repr(self.contents)

    def append(self, card: Card) -> None:
        """Add card to the discard.

        Appends card to the end of the Discard contents.
        Card attributes are modified automatically as part of this process.

        Args:
            card (Card): The card being added.
        """

        card.hidden = False
        card.team = None
        if self.attacker:
            card.face_up = False
        else:
            card.face_up = True
        self.contents.append(card)

    def display(self) -> str:
        """Return the discard as displayed to players."""
        if len(self.contents) != 0:
            return repr(self.contents[-1])
        else:
            return "--"

    def recycle(self) -> list[Card]:
        """Recycle the discard.

        Clears the discard and returns the shuffled contents.
        Used by decks when being drawn from whilst empty.

        Returns:
            list[Card]: Shuffled discard contents.
        """

        out = self.contents.copy()
        shuffle(out)
        self.contents.clear()
        return out


class Deck:
    """A BINMAT deck.

    Contains a collection of Card objects, with methods for displaying contents and drawing from the deck.

    Drawing from an empty deck will attempt to shuffle in the contents of the associated discard, and then draw.

    Attributes:
        contents (list[Card]): The collection of BINMAT cards in the deck.
        visible (bool): If the top card of the deck is visible. Typically used for the decks of lanes 3, 4, and 5.
        discard (Discard | None): The deck's associated discard. Used when a draw is attempted when the deck is empty.
    """

    def __init__(
        self,
        contents: list[Card],
        discard: Discard | None = None,
        visible: bool = False,
    ) -> None:
        """Create a BINMAT deck.

        Args:
            contents (list[Card]): Deck contents.
            discard (Discard | None, optional): The deck's associated discard. Defaults to None.
            visible (bool, optional): If the top card is visible. Defaults to False.
        """

        self.contents = contents
        self.visible = visible
        self.discard = discard

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)

    def __repr__(self) -> str:
        return repr(self.contents)

    def display(self) -> str:
        """Return the deck as displayed to players."""
        if len(self.contents) != 0:
            if self.visible:
                return repr(self.contents[-1])
            else:
                return "X"
        else:
            return "--"

    def draw(self) -> Card:
        """Draw a card from the deck."""

        return self.contents.pop()


class Whole_Deck:
    def __init__(self) -> None:
        self.contents = [].copy()
        for axiom in AXIOMS:
            for value in CARD_VALUES:
                self.contents.append(Card(axiom, value))

    def generate_lane_decks(self):
        shuffled_contents = deepcopy(self.contents)
        lane_decks: list[Deck] = [].copy()
        shuffle(shuffled_contents)
        for offset in range(6):
            start = offset * 13
            lane_decks.append(Deck(shuffled_contents[start : start + 13]))
        for deck in lane_decks[3:]:
            deck.visible = True
        return lane_decks


class Stack:
    def __init__(self, team: int = 0) -> None:
        self.team = team
        self.contents: list[Card] = [].copy()

    def display(self, team: int | None = None):
        out = [].copy()
        for card in self.contents:
            if team is not None:
                out.append(card.display(team))
            else:
                out.append(repr(card))
        return " ".join(out)

    def __repr__(self) -> str:
        return repr(self.contents)

    def append(self, card: Card):
        card.team = self.team
        self.contents.append(card)

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)


class Lane:
    def __init__(self, number: int, deck: Deck, attacker: bool = False) -> None:
        self.number = number
        self.deck = deck
        self.attacker = attacker
        self.discard = Discard(attacker)
        self.deck.discard = self.discard
        self.d = Stack(TEAMS["defender"])
        self.a = Stack(TEAMS["attacker"])
        self.stacks = [self.d, self.a]

    def __str__(self):
        return f"l{self.number}: {self.deck.display()}\nx{self.number}: {self.discard.display()}\nd{self.number}: {self.d.display()}\na{self.number}: {self.a.display()}"

    def combat(self, declaring_team: int):
        stacks = [self.d, self.a]
        if not stacks[declaring_team]:
            raise InvalidOp("Cannot declare combat with your stack empty.")


class Hand:
    def __init__(self) -> None:
        self.contents = [].copy()

    def __repr__(self) -> str:
        return repr(self.contents)

    def display(self, team: int | None = None):
        out = [].copy()
        for card in self.contents:
            if team is not None:
                out.append(card.display(team))
            else:
                out.append(repr(card))
        return " ".join(out)

    def append(self, card: Card):
        self.contents.append(card)

    def take(self, search: str) -> Card:
        if search in self.contents:
            return self.contents.pop(self.contents.index(search))
        else:
            raise LookupError(f"{search} not in hand")

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)


class Player:
    def __init__(self, team: int, ind: int, name: str = "") -> None:
        self.team = team
        self.ind = ind
        self.label = f"{["d","a"][team]}{hex(ind)[2]}"
        self.name = name
        self.hand = Hand()

        if not self.name:
            self.name = f"{TEAMS[team]}_{hex(ind)[2]}"

    def __repr__(self) -> str:
        return f"{self.label}: {repr(self.hand)}"

    # def __str__(self) -> str:
    #     return f"{self.label}: {repr(self.hand)}"

    def display(self, team: int | None = None):
        return f"{self.label}: {self.hand.display(team)}"

    def draw(self, deck: Deck):
        card = deck.draw()
        card.hidden = True
        card.team = self.team
        card.face_up = False
        self.hand.append(card)

    def place(self, lane: Lane, card: str, face_up: bool = False):
        try:
            selected = self.hand.take(card)
            selected.face_up = face_up
            lane.stacks[self.team].append(selected)
        except LookupError:
            # raise InvalidOp(f"card {card} not in hand")
            print(InvalidOp(f"card {card} not in hand"))

    def discard(self, lane: Lane, card: str):
        try:
            selected = self.hand.take(card)
            lane.discard.append(selected)
        except LookupError:
            # raise InvalidOp(f"card {card} not in hand")
            print(InvalidOp(f"card {card} not in hand"))


class Team:
    def __init__(
        self, team: int, players: list[str] = [].copy(), length: int | None = None
    ) -> None:
        self.team = team

        if length and not players:
            self.players = [].copy()
            for i in range(length):
                self.players.append(Player(self.team, i))
        else:
            self.players = map(
                lambda p: Player(self.team, players.index(p), p), players
            )

    def __str__(self) -> str:
        return "\n".join(map(lambda p: f"{p.label} {p.name}", self.players))


class Op:
    # actions = {"d": "draw", "p": "play", "u": "uplay", "x": "discard", "c": "combat"}
    def __init__(self, acting_player: Player, op: str) -> None:
        self.acting_player = acting_player
        self.op = op

        self.action: Literal["draw", "play", "uplay", "discard", "combat"]
        self.lane: str
        self.card: str | None = None

        try:
            match op[0]:
                case "d":
                    print("draw op")
                    self.action = "draw"
                    self.lane = op[1]
                case "p":
                    print("play op")
                    self.action = "play"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]

                case "u":
                    print("uplay op")
                    self.action = "uplay"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]
                case "x":
                    print("discard op")
                    self.action = "discard"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]
                case "c":
                    print("combat op")
                    self.action = "combat"
                    self.lane = op[1]
                case _:
                    print("unknown action")
                    raise InvalidOp()
        except IndexError:
            raise InvalidOp()


class Turn: ...


class Game: ...


class State: ...


# decks = Whole_Deck().generate_lane_decks()

# lane0 = Lane(0, decks[0])

# d0 = Player(0, 0)
# a0 = Player(1, 0)

# temp = Discard(
#     False,
#     [
#         Card("!", "a"),
#         Card("!", "2"),
#         Card("!", "3"),
#         Card("!", "@"),
#         Card("^", "a"),
#         Card("%", "*"),
#         Card("+", ">"),
#     ],
# )

# print(temp.contents)
# print(temp.recycle())
# print(temp.contents)

# print(Op(d0, "d0").__dict__)
# print(Op(d0, "pa0").__dict__)
# print(Op(d0, "u>0").__dict__)
# print(Op(d0, "x>0").__dict__)
# print(Op(d0, "c0").__dict__)
# print(Op(d0, "pa").__dict__)

# temp_deck = Deck(
#     [Card("!", "2"), Card("!", "3"), Card("!", "4"), Card("!", "5"), Card("%", "5")]
# )

# d0.draw(temp_deck)
# a0.draw(temp_deck)
# d0.draw(temp_deck)
# a0.draw(temp_deck)
# d0.draw(temp_deck)

# print(temp_deck)
# print(d0)
# print(a0)
# print(temp_deck)
# print(lane0)

# print("\n\n\n\n\n")

# d0.place(lane0, "5")
# a0.place(lane0, "5")
# print(lane0)
# d0.place(lane0, "4")
# a0.place(lane0, "4")
# print(lane0)


# print(lane0)
# print(lane0.__dict__)

# temp = [Card("%", "4"), Card("&", "4"), Card("+", "5"), Card("^", "4"), Card("!", "a")]

# print("4" in temp)
# print("4%" in temp)
# print("4!" in temp)

# print(Team(0, length=16))
# print(Team(1, length=16))

# print(Team(0, ["foo", "bar"]))
# print(Team(1, ["xar", "qar"]))
