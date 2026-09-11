Description

Ce script CircuitPython transforme une carte RP2040 (format clé USB) en périphérique HID Keyboard. Une fois branché sur une machine cible Windows, il exécute automatiquement une séquence de frappes clavier simulant un utilisateur humain, en moins de 5 secondes.

La chaîne d'exécution complète :

Ouvre une invite CMD via Win+R
Lance PowerShell avec privilèges administrateur
Valide automatiquement l'UAC
Crée un dossier dédié et l'ajoute aux exclusions Windows Defender
Télécharge un payload distant depuis le serveur C2
L'exécute en mode furtif (-WindowStyle Hidden)
Ferme toutes les fenêtres ouvertes
