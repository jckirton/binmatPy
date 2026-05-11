from random import shuffle
from copy import deepcopy


from .constants import AXIOMS, CARD_VALUES, TEAMS
from .classes import Card, Pile, Discard, Deck, Stack, Lane, Hand, Player, Team, Op
from .errors import GameEnd, InvalidOp


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

    def display(self, team: int) -> str:
        return (
            f"{self.defenders}\n"
            f"{self.attackers}\n"
            "--------------\n"
            f"{"\n".join(map(lambda p: p.display(team), self.defenders))}\n"
            f"{"\n".join(map(lambda p: p.display(team), self.attackers))}\n"
            "--------------\n"
            # f"{"\n".join(map(lambda lane: self.lanes[lane].display(team), self.lanes))}\n"
            f"{str(self.turn).ljust(3, "0")} -----\n"
            f"{self.lanes["0"].discard.display().ljust(3)}{self.lanes["1"].discard.display().ljust(3)}{self.lanes["2"].discard.display().ljust(3)}{self.lanes["3"].discard.display().ljust(3)}{self.lanes["4"].discard.display().ljust(3)}{self.lanes["5"].discard.display().ljust(3)}\n"
            f"{self.lanes["0"].deck.display().ljust(3)}{self.lanes["1"].deck.display().ljust(3)}{self.lanes["2"].deck.display().ljust(3)}{self.lanes["3"].deck.display().ljust(3)}{self.lanes["4"].deck.display().ljust(3)}{self.lanes["5"].deck.display().ljust(3)}\n"
            f"{self.lanes["0"].d.display(team).ljust(3)}{self.lanes["1"].d.display(team).ljust(3)}{self.lanes["2"].d.display(team).ljust(3)}{self.lanes["3"].d.display(team).ljust(3)}{self.lanes["4"].d.display(team).ljust(3)}{self.lanes["5"].d.display(team).ljust(3)}\n"
            f"{self.lanes["0"].a.display(team).ljust(3)}{self.lanes["1"].a.display(team).ljust(3)}{self.lanes["2"].a.display(team).ljust(3)}{self.lanes["3"].a.display(team).ljust(3)}{self.lanes["4"].a.display(team).ljust(3)}{self.lanes["5"].a.display(team).ljust(3)}\n"
        )

    def do_turn(self) -> None:
        acting_team: Team = self.defenders if self.turn % 2 == 0 else self.attackers
        ops: list[Op] = []

        print(self.display(acting_team.team))

        if self.turn == self.max_turns:
            raise GameEnd()

        try:
            for player in acting_team:
                # get op for each player
                ops.append(Op(player, input(f"{player} op: ")))

            print(ops)

            for op in ops:
                match op.action:
                    case "draw":
                        op.acting_player.draw(self.lanes[op.lane].deck)
                    case "play":
                        op.acting_player.place(self.lanes[op.lane], op.card)
                    case "uplay":
                        op.acting_player.place(self.lanes[op.lane], op.card, True)
                    case "discard":
                        op.acting_player.discard(self.lanes[op.lane], op.card)
                    case "combat":
                        raise NotImplementedError()

        except InvalidOp as e:
            print(f"Invalid operation: {e}")

        self.turn += 1
