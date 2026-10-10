const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
let state = null;

const elements = {
  slots: document.querySelector("#word-slots"),
  keyboard: document.querySelector("#keyboard"),
  mistakes: document.querySelector("#mistakes-count"),
  length: document.querySelector("#word-length"),
  message: document.querySelector("#message"),
  status: document.querySelector("#status-text"),
  round: document.querySelector("#round-number"),
  drawing: document.querySelector("#hangman-drawing"),
  score: document.querySelector("#score"),
  reset: document.querySelector("#reset-game")
};

async function request(path, options = {}) {
  const response = await fetch(path, options);
  if (!response.ok) throw new Error("The game server is unavailable.");
  return response.json();
}

function render() {
  const finished = state.status !== "playing";
  elements.slots.innerHTML = state.display_word.map(letter => `<span class="slot">${letter}</span>`).join("");
  elements.length.textContent = `${state.word_length} letters`;
  elements.mistakes.textContent = state.incorrect_guesses.length;
  elements.message.textContent = state.message;
  elements.message.className = `message ${state.status === "won" ? "win" : state.status === "lost" ? "lose" : ""}`;
  elements.status.textContent = state.status === "playing" ? "Game in progress" : state.status === "won" ? "Word found" : "Round over";
  elements.round.textContent = String(state.round).padStart(2, "0");
  elements.score.textContent = String(state.score).padStart(4, "0");
  elements.reset.classList.toggle("visible", finished);
  elements.drawing.classList.toggle("is-lost", state.status === "lost");
  elements.drawing.classList.toggle("is-won", state.status === "won");

  const parts = elements.drawing.querySelectorAll(".person");
  parts.forEach((part, index) => { part.style.opacity = index < state.incorrect_guesses.length ? "1" : "0"; });
  elements.keyboard.innerHTML = alphabet.split("").map(letter => {
    const guessed = state.guessed_letters.includes(letter);
    const correct = guessed && state.word.includes(letter);
    return `<button class="key ${correct ? "correct" : guessed ? "wrong" : ""}" data-letter="${letter}" type="button" ${guessed || finished ? "disabled" : ""}>${letter}</button>`;
  }).join("");
}

async function guess(letter) {
  state = await request("/api/guess", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ letter }) });
  render();
}

document.querySelector("#keyboard").addEventListener("click", event => {
  if (event.target.dataset.letter) guess(event.target.dataset.letter).catch(showError);
});
document.querySelector("#new-game").addEventListener("click", () => {
  request("/api/new", { method: "POST" }).then(nextState => { state = nextState; render(); }).catch(showError);
});
document.querySelector("#reset-game").addEventListener("click", () => {
  request("/api/new", { method: "POST" }).then(nextState => { state = nextState; render(); }).catch(showError);
});

document.addEventListener("keydown", event => {
  const letter = event.key.toUpperCase();
  if (/^[A-Z]$/.test(letter) && state && state.status === "playing" && !state.guessed_letters.includes(letter)) {
    guess(letter).catch(showError);
  }
});

function showError(error) { elements.message.textContent = error.message; elements.message.className = "message lose"; }
request("/api/state").then(nextState => { state = nextState; render(); }).catch(showError);