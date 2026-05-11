from copy import deepcopy


from .constants import AXIOMS, CARD_VALUES, TEAMS
from .classes import *
from .errors import GameEnd

# class Whole_Deck:
#     """The full 78 card BINMAT deck.

#     Used to generate lane decks for game initialisation.
#     """

#     def __init__(self) -> None:
#         self.contents = []
#         for axiom in AXIOMS:
#             for value in CARD_VALUES:
#                 self.contents.append(Card(axiom, value))

#     def generate_lane_decks(self) -> list[Deck]:
#         """Generate lane decks.

#         Creates 6 new decks of 13 cards from a shuffled deep-copy of whole-deck contents.

#         Returns:
#             list[Deck]: List of 6 shuffled decks.
#         """

#         shuffled_contents = deepcopy(self.contents)
#         lane_decks: list[Deck] = []
#         shuffle(shuffled_contents)
#         for offset in range(6):
#             start = offset * 13
#             lane_decks.append(Deck(shuffled_contents[start : start + 13]))
#         for deck in lane_decks[3:]:
#             deck.visible = True
#         return lane_decks


class Game:
    def __init__(
        self,
        defenders: list[str] | int = 1,
        attackers: list[str] | int = 1,
        turns: int = 110,
    ) -> None:
        self.max_turns = 110
        self.cards = []
        self.lanes: dict[str, Lane] = {"a": Lane("a", Deck(), True)}

        self.defenders = Team(0, defenders)
        self.attackers = Team(1, attackers)

        for axiom in AXIOMS:
            for value in CARD_VALUES:
                self.cards.append(Card(axiom, value))

        lane_decks = self.generate_lane_decks()

        for deck in lane_decks:
            lNo = str(lane_decks.index(deck))
            self.lanes[lNo] = Lane(lNo, deck)

        # self.state = (lambda: {"a": {"c": len(self.lanes["a"].deck)}})()

        self.turn = 0

    def generate_lane_decks(self) -> list[Deck]:
        """Generate lane decks.

        Creates 6 new decks of 13 cards from a shuffled deep-copy of whole-deck contents.

        Returns:
            list[Deck]: List of 6 shuffled decks.
        """

        shuffled_cards = deepcopy(self.cards)
        lane_decks: list[Deck] = []
        shuffle(shuffled_cards)
        for offset in range(6):
            start = offset * 13
            lane_decks.append(Deck(shuffled_cards[start : start + 13]))
        for deck in lane_decks[3:]:
            deck.visible = True
        return lane_decks

    def do_turn(self) -> None:
        acting_team: Team = self.defenders if self.turn % 2 == 0 else self.attackers
        ops: list[Op] = []

        if self.turn == self.max_turns:
            raise GameEnd()

        for player in acting_team:
            # get op for each player
            ops.append(Op(player, input(f"{player} op: ")))

        print(ops)

        self.turn += 1
