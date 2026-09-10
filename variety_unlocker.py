#!/usr/bin/env python3
"""
Discord Game Variety Badge Unlocker (115 Clean Games Edition)
Cycles through 115 strictly curated, non-sus, mainstream games
from games.json to maximize your played games count on Discord!
Author: IsDevCan
"""

import os
import sys
import time
import socket
import struct
import json
import uuid
import signal
import subprocess

DIR = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(DIR, "games.json")

running = True

def signal_handler(signum, frame):
    global running
    print("\n[!] Stopping Variety Unlocker...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_discord_socket():
    for base in [os.environ.get("TMPDIR", ""), "/tmp"]:
        if not base:
            continue
        for i in range(10):
            p = os.path.join(base, f"discord-ipc-{i}")
            if os.path.exists(p):
                return p
    return None

def load_games():
    if os.path.exists(GAMES_FILE):
        try:
            with open(GAMES_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def cycle_game(sock_path, game, duration=16):
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(sock_path)

        payload = json.dumps({"v": 1, "client_id": game["id"]}).encode("utf-8")
        s.sendall(struct.pack("<ii", 0, len(payload)) + payload)
        hdr = s.recv(8)
        if len(hdr) < 8:
            s.close()
            return False
        s.recv(struct.unpack("<ii", hdr)[1])

        act = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": os.getpid(),
                "activity": {
                    "name": game["name"],
                    "details": game.get("details", "Playing Online"),
                    "state": game.get("state", "In Game"),
                    "timestamps": {"start": int(time.time()) - 180}
                }
            },
            "nonce": str(uuid.uuid4())
        }
        p = json.dumps(act).encode("utf-8")
        s.sendall(struct.pack("<ii", 1, len(p)) + p)
        hdr = s.recv(8)
        if len(hdr) >= 8:
            s.recv(struct.unpack("<ii", hdr)[1])

        t_end = time.time() + duration
        while running and time.time() < t_end:
            time.sleep(1)

        clear = json.dumps({
            "cmd": "SET_ACTIVITY",
            "args": {"pid": os.getpid(), "activity": None},
            "nonce": str(uuid.uuid4())
        }).encode("utf-8")
        try:
            s.sendall(struct.pack("<ii", 1, len(clear)) + clear)
        except Exception:
            pass
        s.close()
        return True
    except Exception:
        return False

def main():
    print("=" * 65)
    print("🤖 JARVIS PROTOCOL: 115 GAME VARIETY UNLOCKER ENGAGED")
    print("Curated Clean Games Pool : 115 Verified Titles")
    print("Strict Safety Filter     : 100% Non-Sus / Zero NSFW")
    print("Time Per Game            : ~16 seconds")
    print("=" * 65)

    sock_path = get_discord_socket()
    if not sock_path:
        print("[X] Discord desktop is not running! Launch Discord first.")
        sys.exit(1)

    games = load_games()
    if not games:
        print("[X] No games found in games.json.")
        sys.exit(1)

    print(f"[✓] Initialized {len(games)} clean games! Commencing sequence...\n")

    completed = 0
    for idx, game in enumerate(games, 1):
        if not running:
            break
        print(f"[{idx:03d}/{len(games)}] 🎮 Playing: {game['name']}")
        ok = cycle_game(sock_path, game, duration=16)
        if ok:
            completed += 1
            print(f"        ✓ Registered with Discord! ({completed}/{len(games)} complete)")
        else:
            print(f"        ! Skipped {game['name']}")

        if running:
            time.sleep(1)

    print("\n" + "=" * 65)
    print(f"🏆 PROTOCOL COMPLETE: {completed} games registered with Discord!")
    print("=" * 65)

    start_script = os.path.join(DIR, "start.sh")
    if os.path.exists(start_script) and running:
        print("\n[*] Re-engaging 24/7 Hours Grinder Protocol...")
        subprocess.run([start_script, "auto"])

if __name__ == "__main__":
    main()
