import tkinter as tk
from tkinter import ttk
import files
import json
import winreg
import os
import sys

pythonw = sys.executable.replace("python.exe", "pythonw.exe")
# functions
def set_apps(event=None):
    listbox1.delete(0, tk.END)
    seen = set()
    with open(files.log, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" - ")
            if len(parts) == 2:
                time = parts[0]
                name = parts[1]
                if name not in seen:
                    seen.add(name)
                    listbox1.insert(tk.END, f"{time}  |  {name}")
def set_activities(event=None):
    listbox2.delete(0, tk.END)
    seen = {}
    with open(files.log, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" - ")
            if len(parts) == 4 and parts[2] == "closed":
                name = parts[1]
                duration = parts[3]
                seen[name] = duration
    for name, duration in seen.items():
        listbox2.insert(tk.END, f"{name} | {duration}")
def clear_log():
    selected = main.tab(main.select(), "text")
    if selected == "LOG":
        with open(files.log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = [line for line in lines if len(line.strip().split(" - ")) != 2]
        with open(files.log, "w", encoding="utf-8") as f:
            f.writelines(kept)
        set_apps()
    elif selected == "ACTIVITY":
        with open(files.log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = [line for line in lines if len(line.strip().split(" - ")) != 4]
        with open(files.log, "w", encoding="utf-8") as f:
            f.writelines(kept)
        data = {}
        with open("total_time.json", "w") as f:
            json.dump(data, f)
        set_activities()
def delete_line():
    selected_tab = main.tab(main.select(), "text")
    if selected_tab == "LOG":
        selected = listbox1.curselection()
        if not selected:
            return
        item = listbox1.get(selected[0])
        name = item.split("  |  ")[1]
        with open(files.log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = [line for line in lines if name not in line or len(line.strip().split(" - ")) != 2]
        with open(files.log, "w", encoding="utf-8") as f:
            f.writelines(kept)
        set_apps()
    elif selected_tab == "ACTIVITY":
        selected = listbox2.curselection()
        if not selected:
            return
        item = listbox2.get(selected[0])
        name = item.split(" | ")[0]
        with open(files.log, "r", encoding="utf-8") as f:
            lines = f.readlines()
        kept = [line for line in lines if name not in line or len(line.strip().split(" - ")) != 4]
        with open(files.log, "w", encoding="utf-8") as f:
            f.writelines(kept)
        with open("total_time.json", "r") as f:
            data = json.load(f)
        data.pop(name, None)
        with open("total_time.json", "w") as f:
            json.dump(data, f)
        set_activities()
def on_tab_changed(event=None):
    selected = main.tab(main.select(), "text")
    if selected == "LOG":
        set_apps()
    elif selected == "ACTIVITY":
        set_activities()
    elif selected == "SETTINGS":
        with open("settings.json", "r") as f:
            data = json.load(f)
        var.set(data["working"])
def settings_set(varr):
    if varr == "working":
        with open("settings.json", "w") as f:
            json.dump({"working": var.get()}, f)
        if var.get():
            if getattr(sys, 'frozen', False):
                command = f'"{files.path}"'
            else:
                command = f'"{pythonw}" "{files.path}"'
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "AppsTracker", 0, winreg.REG_SZ, command)
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, "AppsTracker")
            except:
                pass
# config window
root = tk.Tk()
root.geometry("500x450")
root.title("Apps Tracker")
root.iconbitmap(files.icon)
root.resizable(False, False)
var = tk.BooleanVar()
# notebook
main = ttk.Notebook(root)
main.pack(fill="both", expand=True)
main.bind("<<NotebookTabChanged>>", on_tab_changed)
# tabs frames
tab_log = ttk.Frame(main)
tab_activity = ttk.Frame(main)
tab_settings = ttk.Frame(main)
# tabs
main.add(tab_log, text="LOG")
main.add(tab_activity, text="ACTIVITY")
main.add(tab_settings, text="SETTINGS")
# titles
tk.Label(tab_log, text="Log", font=("Segoe UI", 30, "italic"), cursor="right_ptr").pack()
tk.Label(tab_activity, text="Activity", font=("Segoe UI", 30, "italic"), cursor="right_ptr").pack()
tk.Label(tab_settings, text="Settings", font=("Segoe UI", 30, "italic"), cursor="right_ptr").pack()
# listboxes
scrollbar1 = tk.Scrollbar(tab_log, cursor="sb_v_double_arrow")
scrollbar1.pack(side="right", fill="y")
listbox1 = tk.Listbox(tab_log, yscrollcommand=scrollbar1.set, font=("Segoe UI", 15), cursor="hand1")
listbox1.pack(side="top", fill="both", expand=True)
scrollbar1.config(command=listbox1.yview)
buttons_frame = tk.Frame(tab_log)
buttons_frame.pack(side="bottom", fill="x", padx=5, pady=5)
clearbut = tk.Button(buttons_frame, text="CLEAR", command=clear_log, bg="red", font=("Segoe UI", 13), cursor="hand2")
delbut = tk.Button(buttons_frame, text="DELETE", bg="red", command=delete_line, font=("Segoe UI", 13), cursor="hand2")
clearbut.grid(row=0, column=0, padx=2)
delbut.grid(row=0, column=1, padx=2)
scrollbar2 = tk.Scrollbar(tab_activity, cursor="sb_v_double_arrow")
scrollbar2.pack(side="right", fill="y")
listbox2 = tk.Listbox(tab_activity, yscrollcommand=scrollbar2.set, font=("Segoe UI", 15), cursor="hand1")
listbox2.pack(side="top", fill="both", expand=True)
scrollbar2.config(command=listbox2.yview)
buttons_frame1 = tk.Frame(tab_activity)
buttons_frame1.pack(side="bottom", fill="x", padx=5, pady=5)
clearbut1 = tk.Button(buttons_frame1, text="CLEAR", command=clear_log, bg="red", font=("Segoe UI", 13), cursor="hand2")
delbut1 = tk.Button(buttons_frame1, text="DELETE", bg="red", command=delete_line, font=("Segoe UI", 13), cursor="hand2")
clearbut1.grid(row=0, column=0, padx=2)
delbut1.grid(row=0, column=1, padx=2)
working = tk.Checkbutton(tab_settings, text="Working", font=("Segoe UI", 20), variable=var, cursor="hand2", command=lambda: settings_set("working"))
working.place(x=15, y=60)
working_desc = tk.Label(tab_settings, text="--Will the program run in the background", font=("Segoe UI", 13), cursor="right_ptr")
working_desc.place(x=150, y=70)
set_apps()
root.mainloop()