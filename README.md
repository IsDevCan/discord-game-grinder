# 🎮 Discord Game Grinder & Variety Badge Unlocker

A lightweight, zero-CPU Discord automation suite that grinds game hours and unlocks the **100+ Game Variety Badge** using Discord's official local IPC protocol (`discord-ipc-0`).

---

## ✨ Features

### ⚔️ 1. Hours Grinder (Golden Sword Badge)
- **Live Match Progression:** Simulates realistic round-by-round scores (`In Match (0 - 0)` -> `7 - 5` -> `13 - 11`).
- **Rotating Maps & Agents:** Automatically cycles through real competitive maps (*Ascent, Bind, Haven, Lotus, Split, Sunset, Icebox*) and agents (*Jett, Reyna, Omen, Sova, Clove, etc.*).
- **Auto-Rotation:** Automatically switches between games (e.g., VALORANT and Fortnite Battle Royale) with post-match lobby breaks.
- **Zero Resource Consumption:** Runs at **0.0% CPU**, zero battery drain, and zero fan noise.

### 🏆 2. 100+ Game Variety Badge Unlocker
- Fetches verified game IDs directly from Discord's official database.
- Automatically cycles through 65+ major games (*Overwatch, WoW, Dota 2, Rainbow Six, Rocket League, Elden Ring, GTA V, etc.*).
- Easily pushes your total games played count past 100 to unlock the **Game Variety Badge**.
- Automatically switches back to the hours grinder once completed.

---

## 🚀 Quick Start

### Start the Hours Grinder (Background)
```bash
./start.sh auto       # Realistic live matches with auto-rotation
./start.sh valorant   # VALORANT only
./start.sh fortnite   # Fortnite only
```

### Check Live Status
```bash
./status.sh
```

### Stop the Grinder
```bash
./stop.sh
```

### Run the 100+ Game Variety Unlocker
```bash
./unlock_variety.sh
./variety_status.sh   # Check unlock progress
```

---

## 🔒 Safety & TOS Compliance
- **No Self-Botting:** Never touches your account token or password.
- **Official IPC Protocol:** Uses Discord's built-in local IPC socket (`discord-ipc-0`), identical to Spotify and official game integrations.
- **Client Integrity:** Does not inject or modify Discord client files.
