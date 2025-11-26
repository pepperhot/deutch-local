# 🎮 DEUTCH - Jeu de Cartes Multijoueur

**Jeu de cartes de mémoire et stratégie en réseau local avec interface graphique moderne**

---

## 🚀 Démarrage Rapide

### 1. Lancer le serveur
```bash
python server.py
```

### 2. Lancer les clients
```bash
python client.py
```

### 3. Jouer
- Entrez votre pseudo
- Cliquez sur "Démarrer le jeu"
- Attendez les autres joueurs et commencez !

---

## 🎯 Règles

**Objectif :** Avoir le score le plus bas possible (5 cartes en main)

### Tour de jeu
1. **Piocher** une carte (pioche ou fosse)
2. **Remplacer** une de vos cartes OU **Jeter** la carte piochée
3. Votre tour se termine automatiquement

### Cartes Spéciales
- **Dame (D)** 👁️ : Voir une de vos cartes cachées (3 sec)
- **Valet (V)** 🔄 : Échanger une carte avec un adversaire
- **10♥/10♦** ⚡ : Forcer un adversaire à prendre votre carte
- **Saute-mouton** 🐑 : Défausser si même valeur que la fosse (sinon +2 cartes)

### Fin de partie
Cliquez sur **DEUTCH** pour déclencher le dernier tour. Le joueur avec le score le plus bas gagne !

---

## 💯 Valeurs des Cartes

| Carte | Points |
|-------|--------|
| As (A) | 1 |
| 2-9 | 2-9 |
| 10, V, D | 10 |
| R♥/R♦ | 0 |
| R♠/R♣ | 90 |

---

## 🌐 Jouer en Réseau Local

Dans `client.py`, modifiez :
```python
HOST = '192.168.1.10'  # IP du serveur
PORT = 5000
```

Trouvez l'IP du serveur : `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)

---

## 🔧 Prérequis

- Python 3.8+
- Tkinter (inclus avec Python, ou `sudo apt-get install python3-tk` sur Linux)

---

## 👥 Contributeurs

**Lucas (pepperhot)** - Développeur principal

---

**Bon jeu ! 🎉**
