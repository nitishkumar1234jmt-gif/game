# Hangman Word Workshop

An internship-ready, text-based Hangman game built with a separate frontend and Python backend.

## Project structure

```text
hang.html          # Browser interface
main/styles.css    # Responsive dark animated design
main/game.js       # Keyboard and API interactions
main/server.py     # Python game state and HTTP API
```

## Features

- Five predefined words selected randomly by Python
- Six incorrect guesses per round
- On-screen and physical keyboard input
- Win, loss, new-round, and responsive mobile states
- No external Python packages required

## Run locally

From the project folder, use Python 3:

```powershell
python main/server.py
```

Open `http://127.0.0.1:8000/hang.html` in a browser. The server exposes `/api/state`, `/api/new`, and `/api/guess` for the frontend.