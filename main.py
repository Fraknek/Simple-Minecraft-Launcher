import minecraft_launcher_lib
import subprocess
import os
import customtkinter
import threading
import json
import psutil
import tkinter.messagebox as messagebox
import requests
import time

splash = customtkinter.CTk()
splash.overrideredirect(True)
splash.attributes("-alpha", 0.9)
width = 300
height = 200
screen_width = splash.winfo_screenwidth()
screen_height = splash.winfo_screenheight()
x = int((screen_width / 2) - (width / 2))
y = int((screen_height / 2) - (height / 2))
splash.geometry(f"{width}x{height}+{x}+{y}")
splash.title("Minecraft Launcher")
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
label = customtkinter.CTkLabel(splash, text="Simple Minecraft Launcher is\nLoading...", font=("Arial", 20))
label.pack(expand=True)
splash.update()
time.sleep(3)
splash.destroy()

APP_VERSION = "1.1"
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.attributes("-alpha", 0.97)

width = 500
height = 550
root.overrideredirect(True)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = int((screen_width / 2) - (width / 2))
y = int((screen_height / 2) - (height / 2))
root.geometry(f"{width}x{height}+{x}+{y}")
root.title("Minecraft Launcher")

x_offset = 0
y_offset = 0
CONFIG_FILE = "config.json"
mc_dir = os.path.join(os.getcwd(), ".minecraft")

LOCAL_JAVA = os.path.join(os.getcwd(), "java", "bin", "javaw.exe")        # Java 21 - for 1.x versions
LOCAL_JAVA_NEW = os.path.join(os.getcwd(), "java-new", "bin", "javaw.exe") # Java 24+ - for 26.x+ versions

def needs_new_java(version):
    try:
        major = int(version.split(".")[0])
        return major >= 24
    except:
        return False

def get_java_path(version):
    if needs_new_java(version):
        if os.path.isfile(LOCAL_JAVA_NEW):
            return LOCAL_JAVA_NEW
        return "javaw"
    else:
        if os.path.isfile(LOCAL_JAVA):
            return LOCAL_JAVA
        return "javaw"

_app_closing = False

def safe_destroy():
    global _app_closing
    if _app_closing:
        return
    _app_closing = True
    root.quit()
    root.destroy()

def check_for_updates():
    try:
        url = "https://raw.githubusercontent.com/Fraknek/Simple-Minecraft-Launcher/refs/heads/main/new.version.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        latest_version = data["version"]
        if latest_version != APP_VERSION:
            root.after(0, lambda: messagebox.showinfo(
                "Update",
                f"New Version available!\nYour: {APP_VERSION}\nNewest: {latest_version}"
            ))
    except Exception as e:
        print("Error in checking for update:", e)

def start_move(event):
    global x_offset, y_offset
    x_offset = event.x
    y_offset = event.y

def do_move(event):
    x = root.winfo_x() + event.x - x_offset
    y = root.winfo_y() + event.y - y_offset
    root.geometry(f"+{x}+{y}")

root.bind("<ButtonPress-1>", start_move)
root.bind("<B1-Motion>", do_move)

def save_config():
    data = {"nick": nick_entry.get(), "version": menu.get()}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            nick_entry.insert(0, data.get("nick", ""))
            menu.set(data.get("version", "1.20.1"))

main_frame = customtkinter.CTkFrame(root, corner_radius=25)
main_frame.pack(padx=20, pady=20, fill="both", expand=True)

def open_mc_dir():
    os.startfile(mc_dir)

def modsfolder():
    mods_dir = os.path.join(mc_dir, "mods")
    os.makedirs(mods_dir, exist_ok=True)
    os.startfile(mods_dir)

def is_installed(version):
    return version in [v['id'] for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)]

def is_minecraft_running():
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            if proc.info['name'] == "javaw.exe":
                cmdline = " ".join(proc.info.get('cmdline', []))
                if "minecraft" in cmdline.lower():
                    return True
        except:
            continue
    return False

def update_button():
    if _app_closing:
        return
    version = menu.get()
    if is_installed(version):
        start_btn.configure(text="Play")
    else:
        start_btn.configure(text="Download")

def check_mods_button():
    if _app_closing:
        return
    if os.path.exists(mc_dir):
        Mods_btn.place(y=400, x=130)
    else:
        Mods_btn.place_forget()

def check_openmcdir_button():
    if _app_closing:
        return
    if os.path.exists(mc_dir):
        openmcdir_btn.place(y=435, x=130)
    else:
        openmcdir_btn.place_forget()

def start_mc():
    save_config()
    if is_minecraft_running():
        messagebox.showwarning("Minecraft", "Minecraft is already running!")
        return
    threading.Thread(target=download_and_run, daemon=True).start()

_progress_bar = None
_status_label = None
_install_hint_label = None

def download_and_run():
    global _progress_bar, _status_label, _install_hint_label

    version = menu.get()
    nick = nick_entry.get()

    if not is_installed(version):
        natives_dir = os.path.join(mc_dir, "versions", version, "natives")
        os.makedirs(natives_dir, exist_ok=True)

        if _progress_bar is None:
            _progress_bar = customtkinter.CTkProgressBar(main_frame, width=250, fg_color="white", progress_color="green")
        if _status_label is None:
            _status_label = customtkinter.CTkLabel(main_frame, text="Status:", font=("Arial", 14))
        if _install_hint_label is None:
            _install_hint_label = customtkinter.CTkLabel(
                main_frame,
                text="After Installation, Minecraft will open automatically!",
                font=("Arial", 18),
                text_color="red"
            )

        root.after(0, lambda: _status_label.place(y=220, x=210))
        root.after(0, lambda: _progress_bar.place(y=250, x=105))
        root.after(0, lambda: _progress_bar.set(0))
        root.after(0, lambda: _install_hint_label.place(y=465, x=40))

        def set_progress(v):
            if not _app_closing:
                root.after(0, lambda: _progress_bar.set(v / 100))

        callback = {"setProgress": set_progress}
        minecraft_launcher_lib.install.install_minecraft_version(version, mc_dir, callback=callback)

        if not _app_closing:
            root.after(0, lambda: _progress_bar.place_forget())
            root.after(0, lambda: _status_label.place_forget())
            root.after(0, lambda: _install_hint_label.place_forget())
            root.after(0, update_button)

    java_path = get_java_path(version)

    options = {
        "username": nick if nick else "Player",
        "uuid": "12345678-1234-1234-1234-1234567890ab",
        "token": "0",
        "executablePath": java_path,
        # FIX: explicitly set JVM memory flags so newer versions don't fail
        # with "could not create java virtual machine" due to insufficient heap
        "jvmArguments": ["-Xmx2G"]
    }
    runninglabel = customtkinter.CTkLabel(main_frame, text="Running...", font=("Arial", 15), text_color="red")
    runninglabel.place(y=250, x=200)
    command = minecraft_launcher_lib.command.get_minecraft_command(version, mc_dir, options)
    process = subprocess.Popen(command)

    if not _app_closing:
        root.after(0, check_mods_button)
        root.after(0, check_openmcdir_button)

    def wait_and_close():
        process.wait()
        if not _app_closing:
            root.after(0, safe_destroy)

    threading.Thread(target=wait_and_close, daemon=True).start()


title = customtkinter.CTkLabel(main_frame, text="Simple Minecraft Launcher", font=("Arial", 28, "bold"))
title.pack(pady=(20, 10))
subtitle = customtkinter.CTkLabel(main_frame, text="by Fraknek", font=("Arial", 10, "bold"))
subtitle.place(y=50, x=350)
customtkinter.CTkLabel(main_frame, text="Nick", font=("Arial", 20)).pack()
nick_entry = customtkinter.CTkEntry(main_frame, width=250, height=40, corner_radius=15, placeholder_text="Default nick is Player")
nick_entry.pack(pady=10)
versionlabel = customtkinter.CTkLabel(main_frame, text=APP_VERSION, font=("Arial", 13))
versionlabel.place(y=480, x=10)

predefined_versions = [
    "1.8.9","1.9","1.9.4","1.10.2","1.11","1.11.2","1.12","1.12.1","1.12.2",
    "1.13","1.13.1","1.13.2","1.14","1.14.1","1.14.2","1.14.3","1.14.4",
    "1.15","1.15.1","1.15.2","1.16","1.16.1","1.16.2","1.16.3","1.16.4","1.16.5",
    "1.17","1.17.1","1.18","1.18.1","1.18.2","1.19","1.19.1","1.19.2","1.19.3","1.19.4",
    "1.20","1.20.1","1.20.2","1.20.3","1.20.4","1.20.5","1.20.6",
    "1.21","1.21.1","1.21.2","1.21.3","1.21.4","1.21.5","1.21.6","1.21.7",
    "1.21.8","1.21.9","1.21.10","1.21.11",
    "26.1.1","26.1"
]

versions_folder = os.path.join(mc_dir, "versions")
if os.path.exists(versions_folder):
    for folder_name in os.listdir(versions_folder):
        if folder_name not in predefined_versions:
            predefined_versions.append(folder_name)

menu = customtkinter.CTkOptionMenu(
    main_frame,
    values=predefined_versions,
    command=lambda _: update_button(),
    fg_color="blue",
    hover=False,
    height=40,
    width=250
)
menu.place(y=170, x=105)

start_btn = customtkinter.CTkButton(main_frame, text="Start", command=start_mc, width=200, height=50, font=("Arial", 20), corner_radius=20, fg_color="green", hover=False)
start_btn.place(y=280, x=130)

exit_btn = customtkinter.CTkButton(main_frame, text="Exit", command=lambda: (save_config(), safe_destroy()), width=200, height=50, font=("Arial", 20), corner_radius=20, fg_color="red", hover=False)
exit_btn.place(y=340, x=130)

Mods_btn = customtkinter.CTkButton(main_frame, text="Mods", command=modsfolder, width=200, height=25, font=("Arial", 20), corner_radius=20, fg_color="blue", hover=False)
openmcdir_btn = customtkinter.CTkButton(main_frame, text="Open MC Directory", command=open_mc_dir, width=200, height=25, font=("Arial", 20), corner_radius=20, fg_color="blue", hover=False)

load_config()
update_button()
check_mods_button()
check_openmcdir_button()
threading.Thread(target=check_for_updates, daemon=True).start()
root.mainloop()