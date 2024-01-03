import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:5000/",
});

const createDeckAndDraw = async () => {
  const { data } = await api.get("start");
  const players = data.round_info;
  return {
    players: { player1: players[0], player2: players[1] },
    finished: data.finished,
    winner: data.winner,
  };
};

const redrawCardFromDeck = async () => {
  const { data } = await api.get(`draw-cards`);
  const players = data.round_info;
  return {
    players: { player1: players[0], player2: players[1] },
    finished: data.finished,
    winner: data.winner,
  };
};

export { createDeckAndDraw, redrawCardFromDeck };
