import json
import os
import sys

icon = "ico.ico"
log = "apps.log"
path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else "tracker.py")

if not os.path.exists("settings.json"):
    with open("settings.json", "w") as f:
        json.dump({"working": True}, f)

if not os.path.exists("apps.log"):
    open("apps.log", "w").close()

if not os.path.exists("total_time.json"):
    with open("total_time.json", "w") as f:
        json.dump({}, f)