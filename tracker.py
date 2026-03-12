# libraries
import psutil
import time
from datetime import datetime
import logging
import json
import os
import sys
import winreg
import importlib
import files
importlib.reload(files)
import files
log = files.log
path = files.path
# variables
IGNORE = {
    "conhost", "smartscreen",
    "SearchFilterHost", "SearchProtocolHost",
    "svchost", "RuntimeBroker", "WmiPrvSE", "msedge"
}
ignoretimes = {}
active_apps = {}
timer = 0
pythonw = sys.executable.replace("python.exe", "pythonw.exe")
# load
if os.path.exists("total_time.json"):
    with open("total_time.json", "r") as f:
        total_time = json.load(f)
else:
    total_time = {}
# winreg
with open("settings.json", "r") as f:
    data = json.load(f)
if data["working"] == True:
    if getattr(sys, 'frozen', False):
        command = f'"{path}"'
    else:
        command = f'"{pythonw}" "{path}"'
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, "AppsTracker", 0, winreg.REG_SZ, command)
else:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, "AppsTracker")
    except:
        pass
# log config
logging.basicConfig(
    filename=log,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    encoding="utf-8"
)
# functions
def get_processes():
    return {p.pid: p.info['name'].removesuffix(".exe")
            for p in psutil.process_iter(['name', 'pid'])}
def save_total_time():
    with open("total_time.json", "w") as f:
        json.dump(total_time, f)
def is_running(app_name):
    for process in psutil.process_iter(['name']):
        if app_name.lower() in process.info['name'].lower():
            return True
    return False
def get_working():
    with open("settings.json", "r") as f:
        return json.load(f)["working"]
old_processes = get_processes()
# cycle
while True:
    time.sleep(2)
    if get_working():
        new_processes = get_processes()
        # app opened
        for pid, name in new_processes.items():
            if pid not in old_processes and name not in IGNORE:
                print(f"{datetime.now()} - opened: {name}")
                logging.info(name)
                IGNORE.add(name)
                ignoretimes[name] = 6
                active_apps[pid] = {"name": name, "start": datetime.now()}
        # app closed
        for pid, info in list(active_apps.items()):
            if pid not in new_processes:
                duration = datetime.now() - info["start"]
                total_time[info["name"]] = total_time.get(info["name"], 0) + duration.seconds
                minutes = total_time[info["name"]] // 60
                seconds = total_time[info["name"]] % 60
                print(f"{info['name']} - closed, total time: {minutes}m {seconds}s")
                logging.info(f"{info['name']} - closed - {minutes}m {seconds}s")
                del active_apps[pid]
                save_total_time()
        old_processes = new_processes
        # ignore remove
        if timer == 6:
            timer = 0
        to_remove = []
        for name, tim in ignoretimes.items():
            ignoretimes[name] -= 2
            if ignoretimes[name] <= 0:
                to_remove.append(name)
        for name in to_remove:
            ignoretimes.pop(name, None)
            IGNORE.discard(name)
        timer += 2