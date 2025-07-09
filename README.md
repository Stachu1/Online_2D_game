# 🕹️ Simple 2D Multiplayer Shooter

A basic 2D multiplayer game where players move using `WASD` keys and shoot in the direction of their mouse cursor using the left mouse button. Players connect to a central server, and all bullets and player positions are synced in real time.

---

## 🎮 Features

- 🔫 Mouse-aimed shooting
- 👥 Multiplayer support (multiple clients can join/leave)
- 📡 Real-time position and bullet synchronization
- 🎨 Random color assigned to each player
- 🎯 Hit detection with basic scoring

---

## 🚀 Getting Started

### ✅ Prerequisites

- Python 3.8+
- `pygame`

Install dependencies:

```bash
pip install pygame
```

---

### 🖥️ Running the Game

#### 1. Start the Server

Run the server first:

```bash
python server.py
```

The server will automatically bind to your local IP address and port `6968`. It will stay running and accept new connections.

#### 2. Start a Client

From another terminal or machine, start the client:

```bash
python client.py
```

You will be prompted to enter the server's IP address (shown when you start the server). Then, a new player will join the game.

---

## 🎮 Controls

| Action              | Key / Mouse      |
|---------------------|------------------|
| Move Up             | `W`              |
| Move Down           | `S`              |
| Move Left           | `A`              |
| Move Right          | `D`              |
| Shoot               | Left Mouse Click |
| Quit Game           | `Esc` or `X`     |

---

## 🌐 Multiplayer System

- The server maintains a list of active players and their bullets.
- Each client sends its own state (position, bullets) to the server.
- The server replies with all other player data.
- When a player disconnects, they're automatically removed from the game world.

---

## 🧠 Known Limitations

- No collision between players
- No score UI (hits are printed in console only)
- No authentication or player names
- Bullet positions are client-simulated
- Minimal error handling or packet integrity checks

---

## 🛠️ Future Improvements

- Add UI for scores and health
- Use UDP for lower latency
- Improve hit detection and server-side validation
- Add player names and chat
- Persistent game stats or leaderboard

---

## 📸 Screenshots

<img width="1200" alt="image" src="https://github.com/user-attachments/assets/21d721af-fef4-499d-ad4d-ac36c2be3d2f" />
