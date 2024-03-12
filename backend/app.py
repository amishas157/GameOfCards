import logging
from typing import List
import requests

from flask import Flask, jsonify
from flask_cors import CORS
from cachetools import TTLCache
from pydantic import BaseModel

cache = TTLCache(maxsize=100, ttl=300)

app = Flask(__name__)
app.secret_key = "your_secret_key"
CORS(app)


# Set up the logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CardAttributes(BaseModel):
    image: str
    suit: str
    value: int


class GameRoundInfo(BaseModel):
    player_name: str
    score: int
    drawn_card: CardAttributes


class APIResponse(BaseModel):
    round_info: List[GameRoundInfo]
    finished: bool
    winner: str | None


class Card:
    """
    This class represents a single playing card in a given deck.
    """

    def __init__(self, card_info: {}, is_last: bool = False) -> None:
        self.image = card_info["image"]
        self.suit = card_info["suit"]
        self.is_last = is_last

        card_value = card_info["value"]
        if card_value == "TEN":
            self.value = 10
        elif card_value == "JACK":
            self.value = 11
        elif card_value == "QUEEN":
            self.value = 12
        elif card_value == "KING":
            self.value = 13
        elif card_value == "ACE":
            self.value = 14
        else:
            try:
                self.value = int(card_value)
            except Exception as e:
                logging.error(e.message)
                raise ValueError(f"The value {card_value} for card is not supported.")


class DeckOfCardsApiClient:
    """
    This class represents a client to invoke public api deckofcardsapi.
    """

    def __init__(self) -> None:
        self.base_url = "https://deckofcardsapi.com/api/deck"

    def get_deck(self) -> str:
        # TODO: Add error handling to accomodate cases when public API is down.

        resp = requests.get(f"{self.base_url}/new/shuffle/?deck_count=1").json()
        return resp["deck_id"]

    def draw_card(self, deck_id: str) -> Card:
        # TODO: Add error handling to accomodate cases when public API is down.

        resp = requests.get(f"{self.base_url}/{deck_id}/draw/?count=1").json()
        return Card(resp["cards"][0], is_last=(resp["remaining"] == 0))


class Player:
    """
    This class represents a single player playing the game of cards.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.deck_id = None
        self.score = 0

    def set_deck(self, deck_id: str) -> None:
        self.deck_id = deck_id

    def add_score(self, score: int) -> None:
        self.score = self.score + score


class GameRound:
    """
    This class represents a single round in a game of cards. Note that there can be as many rounds in a game as number of cards in a deck.
    """

    def __init__(self) -> None:
        self.drawn_cards_by_players = []

    def add_drawn_card_to_player(self, player: Player, card: Card) -> None:
        self.drawn_cards_by_players.append({"player": player, "card": card})

    def find_round_winner(self) -> Player | None:
        assert (
            len(self.drawn_cards_by_players) >= 2
        ), "At least 2 players are needed to play the game."
        if (
            self.drawn_cards_by_players[0]["card"].value
            == self.drawn_cards_by_players[1]["card"].value
        ):
            # Assuming 2 player game
            logging.info("The current round has a tie.")
            return None

        sorted_players = sorted(
            self.drawn_cards_by_players, key=lambda p: p["card"].value, reverse=True
        )
        winner = sorted_players[0]["player"]
        logging.info(f"The winner for current round is {winner.name}.")
        return winner

    def get_info(self) -> [GameRoundInfo]:
        return [
            {
                "player_name": player["player"].name,
                "score": player["player"].score,
                "drawn_card": {
                    "value": player["card"].value,
                    "suit": player["card"].suit,
                    "image": player["card"].image,
                },
            }
            for player in self.drawn_cards_by_players
        ]


class GameOfCards:
    """
    This class represents a game of cards which can contain several rounds.
    """

    def __init__(self, players: []) -> None:
        self.api_caller = DeckOfCardsApiClient()
        self.players = []

        for player in players:
            p = Player(name=player)
            p.set_deck(self.api_caller.get_deck())
            self.players.append(p)

    def find_game_winner(self) -> Player | None:
        cache.clear()

        assert len(self.players) >= 2, "At least 2 players are needed to play the game."
        if self.players[0].score == self.players[1].score:
            # Assuming 2 player game
            logging.info("The game is finished!!!! The match is a tie.")
            return None

        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        winner = sorted_players[0]
        logging.info(
            f"The game is finished!!!! The winner is {winner.name} with score {winner.score}."
        )
        return winner

    def draw_and_compare_cards(self) -> APIResponse:
        is_last_round = False
        game_round = GameRound()
        for player in self.players:
            drawn_card = self.api_caller.draw_card(player.deck_id)
            if drawn_card.is_last:
                is_last_round = True
                logging.info("This is the last round of the game.")

            game_round.add_drawn_card_to_player(player, drawn_card)
            logging.info(
                f"The player {player.name} drew card {drawn_card.suit} and {drawn_card.value}."
            )
        round_winner = game_round.find_round_winner()
        if round_winner:
            round_winner.add_score(1)
            logging.info(f"Adding score 1 to winner {round_winner.name}")

        if is_last_round:
            game_winner = self.find_game_winner()

        return {
            "round_info": game_round.get_info(),
            "finished": is_last_round,
            "winner": game_winner.name if is_last_round and game_winner else None,
        }


@app.route("/")
def default_route():
    response = {"message": "Game of Cards..."}
    return jsonify(response)


@app.route("/start", methods=["GET"])
def start_game():
    logging.info("Starting the game now.")
    game = GameOfCards(players=["A", "B"])
    cache["game"] = game
    response = game.draw_and_compare_cards()
    return jsonify(response)


@app.route("/draw-cards", methods=["GET"])
def draw_cards():
    game = cache.get("game")
    if not game:
        logging.error("No game in progress. Please start a new game to draw a card.")
        return jsonify(
            {"message": "No game in progress. Please start a new game to draw a card."}
        )
    response = game.draw_and_compare_cards()
    return jsonify(response)
