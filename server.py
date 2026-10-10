"""Small standard-library backend for the Hangman game."""

import json
import random
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

WORDS = ["PYTHON", "JOURNEY", "MYSTERY", "KEYBOARD", "SUNSHINE"]
MAX_MISTAKES = 6
ROOT = Path(__file__).resolve().parent.parent
game = {"word": "", "guessed_letters": [], "incorrect_guesses": [], "round": 0, "status": "playing", "score": 0}


def new_game():
    game.update(word=random.choice(WORDS), guessed_letters=[], incorrect_guesses=[], round=game["round"] + 1, status="playing")


def public_state():
    word = game["word"]
    display = [letter if letter in game["guessed_letters"] or game["status"] == "lost" else "" for letter in word]
    if game["status"] == "won":
        message = "Excellent. You found the word!"
    elif game["status"] == "lost":
        message = f"The word was {word}. Try another round."
    else:
        message = "Choose a letter to begin." if not game["guessed_letters"] else "Good thinking. Keep going."
    return {"display_word": display, "word": word, "word_length": len(word), "guessed_letters": game["guessed_letters"], "incorrect_guesses": game["incorrect_guesses"], "round": game["round"], "score": game["score"], "status": game["status"], "message": message}


class GameHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/state":
            self.send_json(public_state())
            return
        if self.path in ("/", "/hang.html", "/main/hang.html"):
            self.serve_file(ROOT / "main" / "hang.html", "text/html")
            return
        if self.path == "/main/styles.css":
            self.serve_file(ROOT / "main" / "styles.css", "text/css")
            return
        if self.path == "/main/game.js":
            self.serve_file(ROOT / "main" / "game.js", "application/javascript")
            return
        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/new":
            new_game()
            self.send_json(public_state())
            return
        if self.path != "/api/guess":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            letter = json.loads(self.rfile.read(length)).get("letter", "").upper()
        except (ValueError, json.JSONDecodeError):
            self.send_json({"error": "Invalid request."}, 400)
            return
        if len(letter) != 1 or letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.send_json({"error": "Please send one letter."}, 400)
            return
        if game["status"] != "playing" or letter in game["guessed_letters"]:
            self.send_json(public_state())
            return
        game["guessed_letters"].append(letter)
        if letter not in game["word"]:
            game["incorrect_guesses"].append(letter)
        if all(character in game["guessed_letters"] for character in game["word"]):
            game["status"] = "won"
            game["score"] += 100
        elif len(game["incorrect_guesses"]) >= MAX_MISTAKES:
            game["status"] = "lost"
        self.send_json(public_state())

    def serve_file(self, path, content_type):
        try:
            body = path.read_bytes()
        except FileNotFoundError:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    new_game()
    server = ThreadingHTTPServer(("127.0.0.1", 8000), GameHandler)
    print("Hangman is running at http://127.0.0.1:8000/hang.html")
    server.serve_forever()