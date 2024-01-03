import React from "react";
import Card from "./Card";
import styles from "./GameLayout.scss";
import { createDeckAndDraw, redrawCardFromDeck } from "../service/api";

class GameLayout extends React.Component {
  state = {
    player1: {},
    player2: {},
    button: "Start game",
    loading: false,
    finished: false,
    game: false,
    winner: "",
  };

  componentDidMount = async () => {
    this.setState({ loading: true });
  };

  onButtonClick = async () => {
    const { game } = this.state;

    if (!game) {
      const { players } = await createDeckAndDraw();
      this.setState({
        player1: players.player1,
        player2: players.player2,
        button: "Draw card",
        game: true,
      });
    } else {
      const { players, finished, winner } = await redrawCardFromDeck();

      this.setState({
        player1: players.player1,
        player2: players.player2,
        button: "Draw card",
        finished: finished,
        winner: winner,
      });
    }
  };

  render() {
    const { loading, player1, player2, button, finished, winner, game } = this.state;
    if (!loading) {
      return;
    }
    if (loading && !game) {
      return <button onClick={this.onButtonClick}>{button}</button>
    }
    if (finished) {
      let finishStatement = `Winner is player ${winner}`;
      if (!winner) {
        finishStatement = 'The match is a tie.';
      }

      return (
      <div style={styles.container}>
        <Card
          title={player1.player_name}
          image={player1.drawn_card.image}
          score={player1.score}
        />
        <Card
          title={player2.player_name}
          image={player2.drawn_card.image}
          score={player2.score}
        />
        <div>{finishStatement}</div>
      </div>)
    }
    return (
      <div style={styles.container}>
        <Card
          title={player1.player_name}
          image={player1.drawn_card.image}
          score={player1.score}
        />
        <Card
          title={player2.player_name}
          image={player2.drawn_card.image}
          score={player2.score}
        />
        <button onClick={this.onButtonClick}>{button}</button>
      </div>
    );
  }
}

export default GameLayout;
