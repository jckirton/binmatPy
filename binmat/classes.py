from random import shuffle
from typing import Literal

from .constants import TEAMS, CARD_NUM_VALUES
from .errors import InvalidOp, DrainedDeck

# __all__ = [
#     "Card",
#     "Pile",
#     "Discard",
#     "Deck",
#     "Stack",
#     "Lane",
#     "Hand",
#     "Player",
#     "Team",
#     "Op",
# ]


class Card:
    """A BINMAT card.

    Contains all information about card state.

    Attributes:
        axiom (str): The card's suit, typically one of "%", "&", "+", "!", "^", "#".
        value (str): The value of the card, in symbol form ("@" and not "TRAP", etc.).
        hidden (bool): If the card is hidden. Card is visible to all parties when False.
        face_up (bool): If the card is face-up. Face-up cards are always visible, overriding being hidden.
        team (int | None): If the card is in the posession of a team, as defined in constants.TEAMS. Posessing teams are able to see hidden cards.
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
        if self.face_up:
            return f"{self.value}{self.axiom}u"
        elif self.hidden:
            return f"{self.value}{self.axiom}x"
        else:
            return f"{self.value}{self.axiom}"

    def __str__(self) -> str:
        return self.display()

    def __eq__(self, value: object) -> bool:
        if type(value) is str:
            return value in f"{self.value}{self.axiom}"
        # elif type(value) is Card:
        #     return self.axiom == value.axiom and self.value == value.value
        else:
            return self is value

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


class Pile:
    """Base class for a collection of Card objects."""

    def __init__(self, contents: list[Card] | None = None) -> None:
        self.contents = contents if contents else []

    def __len__(self) -> int:
        return len(self.contents)

    def __bool__(self) -> bool:
        return bool(self.contents)

    def __repr__(self) -> str:
        return repr(self.contents)

    def __contains__(self, item: object) -> bool:
        return item in self.contents

    def __iter__(self):
        return iter(self.contents)

    def append(self, card: Card) -> None:
        self.contents.append(card)

    def pop(self, index: int = -1) -> Card:
        return self.contents.pop(index)

    def count(self, value) -> int:
        return self.contents.count(value)

    def extend(self, iterable) -> None:
        for item in iterable:
            self.append(item)

    def clear(self) -> None:
        self.contents = []

    def index(self, value) -> int:
        return self.contents.index(value)


class Discard(Pile):
    """A BINMAT discard.

    Contains a collection of Card objects, with methods for adding to and displaying contents.

    Attributes:
        contents (list[Card]): The collection of BINMAT cards in the discard.
        attacker (bool): If the discard is an attacker discard. This changes if the card is set to be face-up.
    """

    def __init__(self, attacker: bool = False) -> None:
        """Create a BINMAT discard.

        Args:
            attacker (bool, optional): If the discard is an attacker discard. Defaults to False.
            contents (list[Card], optional): Discard contents. Defaults to [].
        """

        # self.contents: list[Card] = contents
        self.contents: list[Card] = []
        self.attacker: bool = attacker

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)

    def __repr__(self) -> str:
        return repr(self.contents)

    def append(self, card: Card) -> None:
        """Add card to the discard.

        Appends card to the end of the discard's contents.
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
            if self.attacker:
                return " ".join(map(lambda c: c.display(), self.contents))
            else:
                return repr(self.contents[-1])
        else:
            return ""

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
        contents: list[Card] | None = None,
        discard: Discard | None = None,
        visible: bool = False,
    ) -> None:
        """Create a BINMAT deck.

        Args:
            contents (list[Card]): Deck contents. Defaults to []
            discard (Discard | None, optional): The deck's associated discard. Defaults to None.
            visible (bool, optional): If the top card is visible. Defaults to False.
        """

        self.contents = contents if contents is not None else []
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
            return "---"

    def draw(self) -> Card:
        """Draw a card from the deck.

        Card is set to be hidden and not face-up.
        Ownership is not updated.

        Raises:
            DrainedDeck: Draw not possible due to deck and associated discard being empty.

        Returns:
            Card: The drawn card.
        """

        if not self.contents:
            if not self.discard:
                raise DrainedDeck()
            else:
                self.contents = self.discard.recycle()

        drawn = self.contents.pop()
        drawn.face_up = False
        drawn.hidden = True
        return drawn


class Stack(Pile):
    """A BINMAT stack.

    Contains a collection of Card objects, information on team association, and methods for displaying and placing cards to the stack.

    Attributes:
        contents (list[Card]): Stack contents.
        team (int): The stack's associated team, as defined in constants.TEAMS. Affects how cards are updated on placement.
    """

    def __init__(self, team: int = 0) -> None:
        """Create a BINMAT stack.

        Args:
            team (int, optional): Associated team. Defaults to 0 (defender).
        """

        self.team = team
        super().__init__()

    def display(self, team: int | None = None) -> str:
        """Return the stack as displayed to the given team.

        Args:
            team (int | None, optional): The "viewing" team, as defined in constants.TEAMS. Defaults to None.
        """

        # out = []
        # for card in self.contents:
        #     if team is not None:
        #         out.append(card.display(team))
        #     else:
        #         out.append(repr(card))
        # return " ".join(out)
        return self.contents[-1].display(team) if len(self.contents) > 0 else ""

    def append(self, card: Card) -> None:
        """Add card to top of stack.

        Appends card to the end of the stack's contents.
        Card is hidden and ownership is set to stack's team, but facing is unchanged.

        Args:
            card (Card): The card being added.
        """

        card.team = self.team
        card.hidden = True
        self.contents.append(card)

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)

    def __repr__(self) -> str:
        return repr(self.contents)

    def __iter__(self):
        return iter(self.contents)

    def __int__(self) -> int:
        from math import log2

        power = 0
        value = 0
        wild_count = 0
        for card in self.contents:
            value += CARD_NUM_VALUES[card.value]
            if card.value == "*":
                wild_count += 1

        power = log2(value) if value > 0 else 0

        power += wild_count

        if power % 1 != 0 and not wild_count:
            power = 0

        return int(power)

    def __gt__(self, other) -> bool:
        if type(other) == Stack:
            return int(self) > int(other)
        else:
            return int(self) > other

    def __eq__(self, value: object) -> bool:
        if type(value) == Stack:
            return int(self) == int(value)
        else:
            return int(self) == value

    def __ge__(self, other) -> bool:
        if type(other) == Stack:
            return int(self) >= int(other)
        else:
            return int(self) >= other

    def __sub__(self, other):
        if type(other) == Stack:
            return int(self) - int(other)
        else:
            return int(self) - other

    def __add__(self, other):
        if type(other) == Stack:
            return int(self) + int(other)
        else:
            return int(self) + other


class Lane:
    """A BINMAT lane

    Contains a lane "number", a deck, a discard, two stacks, and info on if it's an "attacker" lane.

    Attributes:
        number (str): The lane's "number". Mainly exists for debugging and internal reference.
        deck (Deck): The lane deck.
        discard (Discard): The lane discard.
        d (Stack): The defender stack.
        a (Stack): The attacker stack.
        stacks (list[Stack]): The defender and attacker stacks in that order. Intended for referencing using team numbers.
        attacker (bool): If the lane is an attacker pseudo-lane. Is passed for Discard creation.
    """

    class Resolution:
        def __init__(self):
            self.to_xa = []
            self.to_xl = []
            self.damage = 0
            self.bounce = False
            self.defender_win = False

    def __init__(self, number: str, deck: Deck, attacker: bool = False) -> None:
        """Create a BINMAT lane.

        Takes a lane "number" and deck.
        A discard is created, and set as the deck's associated discard.

        Args:
            number (str): Lane ID.
            deck (Deck): The lane deck.
            attacker (bool, optional): If lane is attacker lane.. Defaults to False.
        """

        self.number = number
        self.deck = deck
        self.attacker = attacker
        self.discard = Discard(attacker)
        self.deck.discard = self.discard
        self.d = Stack(TEAMS["defender"])
        self.a = Stack(TEAMS["attacker"])
        self.stacks = [self.d, self.a]

    def __str__(self):
        return self.display()

    def display(self, team: int | None = None) -> str:
        if self.attacker:
            return f"{f"{self.number} {self.deck.display()}\n" if self.deck else ""}{f"x{self.number} {self.discard.display()}\n" if self.discard else ""}"
        return f"l{self.number}: {self.deck.display()}\nx{self.number}: {self.discard.display()}\nd{self.number}: {self.d.display(team)}\na{self.number}: {self.a.display(team)}"

    def combat(self, declaring_team: int) -> Resolution:
        """Declare combat in the lane.

        Args:
            declaring_team (int): The team declaring combat, as defined in constants.TEAMS.

        Raises:
            InvalidOp: Combat decleration was invalid.
        """

        # raise NotImplementedError()

        resolution = self.Resolution()

        stacks = [self.d, self.a]
        if not stacks[declaring_team]:
            raise InvalidOp("Cannot declare combat with your stack empty.")

        discarded = [[], []]

        for _ in range(stacks[declaring_team].count("@")):
            discarded[not declaring_team].append(stacks[not declaring_team].pop())
        for _ in range(stacks[not declaring_team].count("@")):
            discarded[declaring_team].append(stacks[declaring_team].pop())

        for card in stacks[declaring_team]:
            if card == "?":
                discarded[declaring_team].append(
                    stacks[declaring_team].pop(stacks[declaring_team].index(card))
                )
                resolution.bounce = True
        for card in stacks[not declaring_team]:
            if card == "?":
                discarded[not declaring_team].append(
                    stacks[not declaring_team].pop(
                        stacks[not declaring_team].index(card)
                    )
                )
                resolution.bounce = True

        # for stack in stacks:
        #     if "?" in stack:
        #         resolution.bounce = True
        #         return resolution

        resolution.to_xa.extend(discarded[0])
        resolution.to_xl.extend(discarded[1])

        if resolution.bounce or (self.a == 0 and self.d == 0):
            resolution.bounce = True
            return resolution
        if self.a >= self.d:
            if ">" in self.a or ">" in self.d:
                print("break damage")
                resolution.damage = max(int(self.a), len(self.d))
            else:
                print("non-break damage")
                resolution.damage = (self.a - self.d) + 1
        elif self.a < self.d:
            # discarded[TEAMS["a"]].extend(self.a)
            # self.a.clear()
            resolution.defender_win = True

        return resolution


class Hand:
    """A BINMAT hand.

    A collection of cards held by a player. Has methods for appending cards, and searching for cards based on a given search string (e.g. "9" or "a%").

    Attributes:
        contents (list[Card]): Hand contents.
    """

    def __init__(self, team: int) -> None:
        """Create a BINMAT hand."""

        self.contents = []
        self.team = team

    def __repr__(self) -> str:
        return repr(self.contents)

    def display(self, team: int | None = None) -> str:
        """Return the hand as displayed to the given team.

        Args:
            team (int | None, optional): The "viewing" team, as defined in constants.TEAMS. Defaults to None.
        """

        if team != self.team:
            return str(len(self))

        out = []
        for card in self.contents:
            out.append(card.display(team))
        return " ".join(out)

    def append(self, card: Card) -> None:
        """Add card to hand.

        Appends card to end of the hand contents.

        Args:
            card (Card): The card being added.
        """

        self.contents.append(card)

    def take(self, search: str) -> Card:
        """Take card from hand based on given search string.

        Removes card from hand contents and returns the removed card. Like popping from a list.

        Args:
            search (str): Card to search for, using value ("9") or value and suit ("9%").

        Raises:
            LookupError: Search found no matches in hand contents.

        Returns:
            Card: The matched card.
        """

        if search in self.contents:
            return self.contents.pop(self.contents.index(search))
        else:
            raise LookupError(f"{search} not in hand")

    def __len__(self):
        return len(self.contents)

    def __bool__(self):
        return bool(self.contents)


class Player:
    """A BINMAT player.

    Has a hand, identifying information, and methods for interacting with decks, discards, and stacks.

    Attributes:
        name (str): Player username.
        team (int): Aligned team, as defined in constants.TEAMS.
        ind (int): Index within team.
        label (str): Label of player, as displayed in team list and binlog.
        hand (Hand): The player's hand.
    """

    def __init__(self, team: int, ind: int, name: str = "") -> None:
        """Create a BINMAT player

        Args:
            team (int): Aligned team, as defined in constants.TEAMS
            ind (int): Index in team.
            name (str, optional): Player name, generated if none is given. Defaults to "".
        """

        self.team = team
        self.ind = ind
        self.label = f"{["d","a"][team]}{hex(ind)[2]}"
        self.name = name
        self.hand = Hand(self.team)

        if not self.name:
            self.name = f"{TEAMS[team]}_{hex(ind)[2]}"

    def __repr__(self) -> str:
        return self.label

    def __str__(self) -> str:
        return f"{self.label}: {repr(self.hand)}"

    def __bool__(self) -> bool:
        return bool(self.hand)

    # def __str__(self) -> str:
    #     return f"{self.label}: {repr(self.hand)}"

    def display(self, team: int | None = None) -> str:
        """Return the player as displayed to the given team.

        Args:
            team (int | None, optional): The "viewing" team, as defined in constants.TEAMS. Defaults to None.
        """

        return f"h{self.label} {self.hand.display(team)}"

    def draw(self, deck: Deck) -> None:
        """Draw a card from a given deck.

        Runs deck.draw(), sets attributes of drawn card, and adds card to the player's hand.

        Args:
            deck (Deck): The deck to draw from.
        """

        card = deck.draw()
        card.hidden = True
        card.team = self.team
        card.face_up = False
        self.hand.append(card)

    def place(self, lane: Lane, card: str, face_up: bool = False):
        """Place a card in a target lane.

        Takes a card from the player's hand, and places it in a lane in the appropriate stack.

        Args:
            lane (Lane): The lane being targeted.
            card (str): The card to take from the hand, as passed to Hand.take.
            face_up (bool, optional): If the card is to be played face-up. Defaults to False.

        Raises:
            InvalidOp: The requested card does not exist in the player's hand.
        """

        try:
            if lane.attacker:
                raise InvalidOp("cannot play cards to the attacker pseudo-lane")
            selected = self.hand.take(card)
            selected.face_up = face_up
            lane.stacks[self.team].append(selected)
        except LookupError:
            # raise InvalidOp(f"card {card} not in hand")
            print(InvalidOp(f"card {card} not in hand"))

    def discard(self, lane: Lane, card: str):
        """Discard a card to a target lane.

        Takes a card from the player's hand, and places it in a lane's discard.

        Args:
            lane (Lane): The lane being targeted.
            card (str): The card to take from the hand, as passed to Hand.take.

        Raises:
            InvalidOp: The requested card does not exist in the player's hand.
        """

        try:
            selected = self.hand.take(card)
            lane.discard.append(selected)
        except LookupError:
            # raise InvalidOp(f"card {card} not in hand")
            print(InvalidOp(f"card {card} not in hand"))


class Team:
    """A BINMAT team.

    Has a collection of players.

    Attributes:
        team (int): Team alignment, as defined in constants.TEAMS.
        players (list[Player]): Players in the team.
    """

    def __init__(self, team: int, players: list[str] | int = 0) -> None:
        """Create a BINMAT team.

        Can take either a list of player names, or a number of players to automatically generate.

        Args:
            team (int): Team alignment, as defined in constants.TEAMS.
            players (list[str], optional): Players in team as a list of names or number of players. Defaults to 0.
        """

        self.team: int = team
        self.players: list[Player]

        if type(players) == int:
            self.players = []
            for i in range(players):
                self.players.append(Player(self.team, i))
        elif type(players) == list:
            self.players = list(
                map(lambda p: Player(self.team, players.index(p), p), players)
            )

    def __str__(self) -> str:
        return "\n".join(map(lambda p: f"{p.label} {p.name}", self.players))

    def __iter__(self):
        return iter(self.players)

    def __getitem__(self, key):
        return self.players[key]

    def __len__(self):
        return len(self.players)


class Op:
    """A BINMAT op.

    Takes an op given by the user, and parses information about the requested move.

    Attributes:
        acting_player (Player): The player submitting the op.
        op (str): The op originally given.
        action (str): The action parsed from the op.
        lane (str): The target lane identifier.
        card (str | None): The target card identifier, as would be passed into Hand.take.
    """

    def __init__(self, acting_player: Player, op: str) -> None:
        """Parse a BINMAT op.

        Args:
            acting_player (Player): Player submitting op.
            op (str): Raw op, as given by the user.

        Raises:
            InvalidOp: The given op could not be parsed.
        """

        self.acting_player = acting_player
        self.op = op

        self.action: Literal["draw", "play", "uplay", "discard", "combat"]
        self.lane: str
        self.card: str = ""

        try:
            match op[0]:
                case "d":
                    # print("draw op")
                    self.action = "draw"
                    self.lane = op[1]
                case "p":
                    # print("play op")
                    self.action = "play"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]

                case "u":
                    # print("uplay op")
                    self.action = "uplay"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]
                case "x":
                    # print("discard op")
                    self.action = "discard"
                    match op[2]:
                        case "%" | "&" | "+" | "!" | "^" | "#":
                            self.card = op[1:2]
                            self.lane = op[3]
                        case _:
                            self.card = op[1]
                            self.lane = op[2]
                case "c":
                    # print("combat op")
                    self.action = "combat"
                    self.lane = op[1]
                case _:
                    # print("unknown action")
                    raise InvalidOp("unknown action")
        except IndexError:
            raise InvalidOp("insufficient information")

    def __repr__(self) -> str:
        return repr(self.__dict__)
