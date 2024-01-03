## Backend stack

The backend of the game is developed using python flask API. It includes following endpoints.

```
GET / --> home page.
GET /start --> API endpoint to start the game.
GET /draw-cards --> API endpoint to draw cards as part of existing game in session/cache.
```

API response:

```
{
    round_info: {
        player_name: str,
        score: int,
        drawn_card: {
            image: str,
            suit: str,
            value: int,
        }
    }[],
    finished: bool,
    winner: str | None
}
```

### Considerations

The backend makes use of TTL Caching strategy to preserve game data across multiple requests. This could also be achieved using session variables or database commitments in production environment.

The backend is designed to extend beyond 2 player game.

### How to develop

Setup python >= 3.10

```
cd backend
cd deps
pip install -r requirements.txt
cd ..
flask run -> This will run app in localhost: http://127.0.0.1:5000/
```
