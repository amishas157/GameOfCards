import React from "react";
import styles from "./card.scss";

const Card = ({ title, image, score }) => {
  return (
    <div style={styles.container}>
      <img style={styles.image} src={image} />
      <br />
      Score: <div>{score}</div>
      <div style={styles.title}>{title}</div>
    </div>
  );
};

export default Card;
