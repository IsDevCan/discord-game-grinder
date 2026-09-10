#!/usr/bin/env python3
"""
Discord Game Variety Badge Unlocker
Cycles through 65+ unique official games from Discord's detectable games database
to push your played games count past 100 and unlock the 100+ Game Variety Badge!
"""

import os
import sys
import time
import socket
import struct
import json
import uuid
import urllib.request
import signal
import subprocess

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

def fetch_games(count=65):
    print("[*] Fetching verified game IDs from Discord database...")
    url = "https://discord.com/api/v9/applications/detectable"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            games = []
            seen = set()
            for g in data:
                gid = g.get("id")
                name = g.get("name")
                if gid and name and len(name) > 2 and name not in seen:
                    n_lower = name.lower()
                    # Skip generic, broken, or bugged games like Dark Souls
                    if any(bad in n_lower for bad in ["test", "demo", "unknown", "dark souls", "darksouls"]):
                        continue
                    seen.add(name)
                    games.append({"id": str(gid), "name": name})
                if len(games) >= count:
                    break
            return games
    except Exception as e:
        print(f"[!] Error fetching from Discord API: {e}. Using fallback games list.")
        return []

def cycle_game(sock_path, game, duration=18):
    """Connects to Discord, sets activity for `duration` seconds, then cleanly disconnects."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect(sock_path)

        # Handshake
        payload = json.dumps({"v": 1, "client_id": game["id"]}).encode("utf-8")
        s.sendall(struct.pack("<ii", 0, len(payload)) + payload)
        hdr = s.recv(8)
        if len(hdr) < 8:
            s.close()
            return False
        s.recv(struct.unpack("<ii", hdr)[1])

        # Set Activity
        act = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "pid": os.getpid(),
                "activity": {
                    "details": "Playing Online",
                    "state": "In Game",
                    "timestamps": {"start": int(time.time()) - 120}
                }
            },
            "nonce": str(uuid.uuid4())
        }
        p = json.dumps(act).encode("utf-8")
        s.sendall(struct.pack("<ii", 1, len(p)) + p)
        hdr = s.recv(8)
        if len(hdr) >= 8:
            s.recv(struct.unpack("<ii", hdr)[1])

        # Hold the game active for duration seconds
        t_end = time.time() + duration
        while running and time.time() < t_end:
            time.sleep(1)

        # Clear activity
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
    except Exception as e:
        return False

def main():
    print("=" * 65)
    print("🏆 DISCORD 100+ GAME VARIETY BADGE UNLOCKER")
    print("Target: Cycle through 65 distinct verified games to reach 100+")
    print("Time per game: ~18 seconds")
    print("=" * 65)

    sock_path = get_discord_socket()
    if not sock_path:
        print("[X] Discord desktop is not running! Please open Discord and try again.")
        sys.exit(1)

    games = fetch_games(65)
    if not games:
        print("[X] Could not retrieve game list.")
        sys.exit(1)

    print(f"[✓] Retrieved {len(games)} verified games! (Dark Souls excluded)\n")

    completed = 0
    for idx, game in enumerate(games, 1):
        if not running:
            break
        print(f"[{idx:02d}/{len(games)}] 🎮 Playing: {game['name']}")
        ok = cycle_game(sock_path, game, duration=18)
        if ok:
            completed += 1
            print(f"       ✓ Registered with Discord! ({completed}/{len(games)} unlocked)")
        else:
            print(f"       ! Skipped {game['name']}")

        if running:
            time.sleep(2)

    print("\n" + "=" * 65)
    print(f"🎉 SUCCESS! Completed {completed} games in Discord!")
    print("=" * 65)

    # Resume normal grinder
    dir_path = os.path.dirname(os.path.abspath(__file__))
    start_script = os.path.join(dir_path, "start.sh")
    if os.path.exists(start_script) and running:
        print("\n[*] Automatically resuming normal Game Grinder (Valorant/Fortnite)...")
        subprocess.run([start_script, "auto"])

if __name__ == "__main__":
    main()
