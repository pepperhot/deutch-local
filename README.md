# deutch-local

# 🃏 Jeu de Mémoire en Réseau (Python + Tkinter + Sockets)

Ce projet est un jeu de mémoire multijoueur développé en Python, utilisant **Tkinter** pour l'interface graphique et les **sockets TCP** pour la communication réseau. Chaque joueur doit se souvenir de ses cartes et prendre des décisions à son tour. Le but est de remplacer stratégiquement ses cartes pour optimiser son jeu.

## ✨ Fonctionnalités

- Interface graphique simple via Tkinter
- Jeu multijoueur en réseau local via sockets
- Cartes initiales masquées, visibles quelques secondes au début
- Gestion d'une **pioche** et d'une **fosse**
- Tour par tour, un seul joueur peut jouer à la fois
- Cartes uniques pour chaque joueur
- Affichage temps réel des états du jeu côté serveur

## 📁 Structure du projet


## 🧠 Règles du jeu

1. Chaque joueur reçoit 5 cartes aléatoires qu’il peut voir pendant quelques secondes au début.
2. Les cartes sont ensuite masquées.
3. À son tour, un joueur peut :
   - Prendre une carte de la **pioche**
   - Ou prendre la dernière carte de la **fosse**
4. Il doit alors **remplacer une de ses cartes**.
5. La carte remplacée est envoyée à la **fosse**.
6. Les tours s’enchaînent.

## ▶️ Lancement

### 1. Serveur

Lancer sur l’ordinateur hôte :

```bash
python server.py

### 2. client

Lancer sur l’ordinateur client :

```bash
python client.py