#!/usr/bin/env python3
"""
Discord Game Grinder - Realistic Simulation & Rotation Engine
Simulates real ranked matches with dynamic round scores, maps, agents,
and automatic game rotation so your activity looks 100% genuine on Discord.
"""

import os
import sys
import time
import socket
import struct
import json
import uuid
import signal
import random
import argparse

# Game Client IDs
VALORANT_CLIENT_ID = "811469787657928704"
FORTNITE_CLIENT_ID = "432980957394370572"

VALORANT_MAPS = [
    ("ascent", "Ascent"),
    ("bind", "Bind"),
    ("haven", "Haven"),
    ("split", "Split"),
    ("lotus", "Lotus"),
    ("sunset", "Sunset"),
    ("icebox", "Icebox"),
    ("breeze", "Breeze"),
]

VALORANT_AGENTS = [
    ("jett", "Jett"),
    ("reyna", "Reyna"),
    ("omen", "Omen"),
    ("sova", "Sova"),
    ("clove", "Clove"),
    ("cypher", "Cypher"),
    ("fade", "Fade"),
    ("killjoy", "Killjoy"),
    ("raze", "Raze"),
]

running = True

def signal_handler(signum, frame):
    global running
    print("\n[!] Stopping Game Grinder cleanly...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def get_discord_socket():
    # Direct check in user TMPDIR and /tmp
    for base in [os.environ.get("TMPDIR", ""), "/tmp"]:
        if not base:
            continue
        for i in range(10):
            p = os.path.join(base, f"discord-ipc-{i}")
            if os.path.exists(p):
                return p
    return None

class DiscordIPC:
    def __init__(self, client_id):
        self.client_id = str(client_id)
        self.sock = None

    def connect(self):
        sock_path = get_discord_socket()
        if not sock_path:
            return False, "Discord desktop is not running."

        try:
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.settimeout(4)
            self.sock.connect(sock_path)

            payload = json.dumps({"v": 1, "client_id": self.client_id}).encode("utf-8")
            self.sock.sendall(struct.pack("<ii", 0, len(payload)) + payload)

            resp_hdr = self.sock.recv(8)
            if len(resp_hdr) < 8:
                return False, "Short handshake header"
            op, length = struct.unpack("<ii", resp_hdr)
            resp = json.loads(self.sock.recv(length).decode("utf-8"))
            if resp.get("evt") == "ERROR":
                return False, resp.get("data", {}).get("message")
            return True, "Connected"
        except Exception as e:
            self.close()
            return False, str(e)

    def set_activity(self, details, state, start_timestamp, assets=None):
        if not self.sock:
            return False
        try:
            activity = {
                "details": details,
                "state": state,
                "timestamps": {"start": start_timestamp}
            }
            if assets:
                activity["assets"] = assets

            payload = json.dumps({
                "cmd": "SET_ACTIVITY",
                "args": {
                    "pid": os.getpid(),
                    "activity": activity
                },
                "nonce": str(uuid.uuid4())
            }).encode("utf-8")

            self.sock.sendall(struct.pack("<ii", 1, len(payload)) + payload)
            resp_hdr = self.sock.recv(8)
            if len(resp_hdr) < 8:
                return False
            op, length = struct.unpack("<ii", resp_hdr)
            self.sock.recv(length)
            return True
        except Exception:
            return False

    def close(self):
        if self.sock:
            try:
                clear_payload = json.dumps({
                    "cmd": "SET_ACTIVITY",
                    "args": {"pid": os.getpid(), "activity": None},
                    "nonce": str(uuid.uuid4())
                }).encode("utf-8")
                self.sock.sendall(struct.pack("<ii", 1, len(clear_payload)) + clear_payload)
                self.sock.close()
            except Exception:
                pass
            self.sock = None

class ValorantMatchSimulator:
    def __init__(self):
        self.new_match()

    def new_match(self):
        self.map_key, self.map_name = random.choice(VALORANT_MAPS)
        self.agent_key, self.agent_name = random.choice(VALORANT_AGENTS)
        self.my_score = 0
        self.enemy_score = 0
        self.target_win = 13
        self.target_loss = random.randint(7, 11)
        self.we_win = random.choice([True, False])
        if not self.we_win:
            self.target_win, self.target_loss = self.target_loss, 13

        self.match_start = int(time.time())
        self.last_round_time = time.time()
        self.in_lobby = False
        self.lobby_until = 0

    def step(self):
        now = time.time()
        # In Lobby between matches
        if self.in_lobby:
            if now >= self.lobby_until:
                self.new_match()
            else:
                return {
                    "details": "In Lobby",
                    "state": "In Party (1/5) - Queueing",
                    "start": self.match_start,
                    "assets": {
                        "large_image": "v_logo",
                        "large_text": "VALORANT",
                        "small_image": self.agent_key,
                        "small_text": self.agent_name
                    }
                }

        # Check if match is finished
        if (self.my_score >= self.target_win and self.my_score >= 13) or (self.enemy_score >= self.target_loss and self.enemy_score >= 13):
            # Match ended, transition to lobby for 90-180 seconds
            self.in_lobby = True
            self.lobby_until = now + random.randint(90, 180)
            status_text = "Victory (13 - {})" if self.my_score > self.enemy_score else "Defeat ({} - 13)"
            return {
                "details": f"Competitive ({self.map_name})",
                "state": status_text.format(min(self.my_score, self.enemy_score)),
                "start": self.match_start,
                "assets": {
                    "large_image": self.map_key,
                    "large_text": self.map_name,
                    "small_image": self.agent_key,
                    "small_text": self.agent_name
                }
            }

        # Progress round every ~80-120 seconds
        if now - self.last_round_time > random.randint(80, 120):
            self.last_round_time = now
            if self.my_score < self.target_win and (random.random() < 0.55 if self.we_win else random.random() < 0.45):
                self.my_score += 1
            elif self.enemy_score < (self.target_loss if self.we_win else 13):
                self.enemy_score += 1
            else:
                self.my_score += 1

        return {
            "details": f"Competitive ({self.map_name})",
            "state": f"In Match ({self.my_score} - {self.enemy_score})",
            "start": self.match_start,
            "assets": {
                "large_image": self.map_key,
                "large_text": self.map_name,
                "small_image": self.agent_key,
                "small_text": self.agent_name
            }
        }

class FortniteSimulator:
    def __init__(self):
        self.new_game()

    def new_game(self):
        self.match_start = int(time.time())
        self.remaining = 99
        self.last_drop = time.time()
        self.in_lobby = False
        self.lobby_until = 0

    def step(self):
        now = time.time()
        if self.in_lobby:
            if now >= self.lobby_until:
                self.new_game()
            else:
                return {
                    "details": "Battle Royale",
                    "state": "In Lobby - Ready",
                    "start": self.match_start,
                    "assets": {}
                }

        if self.remaining <= 1:
            self.in_lobby = True
            self.lobby_until = now + random.randint(60, 120)
            return {
                "details": "Battle Royale (Solos)",
                "state": "Victory Royale! #1/100",
                "start": self.match_start,
                "assets": {}
            }

        # Drop remaining players every 25-45 seconds
        if now - self.last_drop > random.randint(25, 45):
            self.last_drop = now
            drop = random.randint(2, 6)
            self.remaining = max(1, self.remaining - drop)

        return {
            "details": "Battle Royale (Solos)",
            "state": f"In Match - {self.remaining} Alive",
            "start": self.match_start,
            "assets": {}
        }

def format_duration(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}h {m:02d}m {s:02d}s"

def main():
    parser = argparse.ArgumentParser(description="Realistic Discord Game Grinder")
    parser.add_argument("--game", choices=["valorant", "fortnite", "auto"], default="auto",
                        help="Game mode: valorant, fortnite, or auto (rotates between games realistically)")
    args = parser.parse_args()

    mode = args.game
    current_game = "valorant" if mode in ["valorant", "auto"] else "fortnite"
    val_sim = ValorantMatchSimulator()
    fn_sim = FortniteSimulator()

    current_ipc = None
    session_start = time.time()
    last_game_switch = time.time()
    # If auto, switch games every 2 to 3 hours (e.g. 7200 - 10800 seconds)
    switch_interval = random.randint(7200, 10800)

    print("=" * 65)
    print("🎮 REALISTIC DISCORD GAME GRINDER")
    print(f"Mode         : {mode.upper()} {'(Auto-Rotates games)' if mode == 'auto' else ''}")
    print("Features     : Dynamic match scores, rotating maps, real agents & breaks")
    print("CPU Usage    : 0.0% (Zero heat / battery drain)")
    print("=" * 65)

    while running:
        # Check if it's time to rotate games in auto mode
        if mode == "auto" and (time.time() - last_game_switch > switch_interval):
            new_game = "fortnite" if current_game == "valorant" else "valorant"
            print(f"\n[🔄] Rotating game: {current_game.upper()} -> {new_game.upper()} for realism...")
            if current_ipc:
                current_ipc.close()
                current_ipc = None
            current_game = new_game
            last_game_switch = time.time()
            switch_interval = random.randint(7200, 10800)

        client_id = VALORANT_CLIENT_ID if current_game == "valorant" else FORTNITE_CLIENT_ID

        if current_ipc is None or current_ipc.sock is None:
            current_ipc = DiscordIPC(client_id)
            ok, msg = current_ipc.connect()
            if not ok:
                sys.stdout.write(f"\r[!] Waiting for Discord client... ({msg})")
                sys.stdout.flush()
                time.sleep(5)
                continue
            print(f"\n[✓] Connected to Discord! Active Game: {current_game.upper()}")

        # Get simulated game state
        if current_game == "valorant":
            act_info = val_sim.step()
        else:
            act_info = fn_sim.step()

        # Update activity
        ok = current_ipc.set_activity(
            details=act_info["details"],
            state=act_info["state"],
            start_timestamp=act_info["start"],
            assets=act_info["assets"]
        )
        if not ok:
            print("\n[!] Connection dropped, will reconnect...")
            current_ipc.close()
            current_ipc = None
            time.sleep(3)
            continue

        elapsed = time.time() - session_start
        status_line = f"\r⏳ Total Grind: {format_duration(elapsed)} | Playing: {current_game.upper()} | {act_info['details']} - {act_info['state']}"
        # Pad with spaces to clear previous text
        sys.stdout.write(status_line.ljust(90))
        sys.stdout.flush()

        time.sleep(12)

    if current_ipc:
        current_ipc.close()
    print(f"\n[✓] Session finished. Total grinded: {format_duration(time.time() - session_start)}")

if __name__ == "__main__":
    main()
