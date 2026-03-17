import json
import argparse
import os
from datetime import datetime

STATE_FILE = "pipeline-state.json"

def load_state():
 if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        return json.load(f)
 return {"completed_steps": []}

def save_state(state):
 with open(STATE_FILE, "w") as f:
    json.dump(state, f, indent=2)

if __name__ == "__main__":
 parser = argparse.ArgumentParser()
 parser.add_argument("--action", required=True, choices=["mark", "list", "clear"])
 parser.add_argument("--step", required=False)
 args = parser.parse_args()

 state = load_state()

 if args.action == "mark":
    state["completed_steps"].append({
     "step": args.step,
     "timestamp": datetime.utcnow().isoformat()
     })
    save_state(state)
    print(f"[OK] Step marked as completed: {args.step}")

 elif args.action == "list":
    print("[INFO] Completed steps:")
    for s in state["completed_steps"]:
        print(f" - {s['step']} at {s['timestamp']}")

 elif args.action == "clear":
    save_state({"completed_steps": []})
    print("[OK] State cleared.")