import socket
import json
import tkinter as tk
import threading

HOST = 'localhost'  # ou IP du serveur
PORT = 5000

main_joueur = []
pioche = []
fosse = []
visible_main = []
carte_en_attente = None
selection_initiale = True
numero_joueur = None
tour_actuel = None
dame_used = []

# --- Interface Tkinter ---
root = tk.Tk()
root.title("Jeu de mémoire - Client")

etat_pioche = tk.StringVar()
etat_fosse = tk.StringVar()
etat_tour = tk.StringVar()

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

btn_frame = tk.Frame(main_frame)
btn_frame.pack()

# --- Socket ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def maj_affichage():
    global main_joueur, visible_main

    for widget in btn_frame.winfo_children():
        widget.destroy()

    # Affichage des cartes du joueur
    for i, carte in enumerate(main_joueur):
        texte = carte if visible_main[i] else "❓"
        btn = tk.Button(btn_frame, text=texte, font=("Arial", 12), width=6,
                        command=lambda idx=i: cliquer_carte(idx))
        btn.grid(row=0, column=i, padx=5)

    # Affichage infos pioche/fosse
    etat_pioche.set(f"Pioche : {pioche[0] if pioche else 'vide'}")
    etat_fosse.set(f"Fosse : {fosse[-1] if fosse else 'vide'}")
    if numero_joueur is not None and tour_actuel is not None:
        if numero_joueur == tour_actuel:
            etat_tour.set("À vous de jouer")
        else:
            etat_tour.set("En attente du tour")

    # Si une Dame est en haut de la pioche ou fosse, possibilité de voir une carte
    if numero_joueur == tour_actuel and carte_en_attente is None:
        dame_carte = ""
        if pioche and pioche[0].startswith("D") and pioche[0] not in dame_used:
            dame_carte = pioche[0]
        elif fosse and fosse[-1].startswith("D") and fosse[-1] not in dame_used:
            dame_carte = fosse[-1]

        if dame_carte and visible_main != False:
            for i, visible in enumerate(visible_main):
                if not visible:
                    btn = tk.Button(btn_frame, text=f"👁 Voir {i + 1}", command=lambda idx=i, dc=dame_carte: utiliser_pouvoir_dame(idx, dc))
                    btn.grid(row=1, column=i, pady=5)

def utiliser_pouvoir_dame(index, dame_carte):
    global dame_used, visible_main
    visible_main[index] = True
    dame_used.append(dame_carte)  # Ajoute la dame à la liste des dames utilisées
    maj_affichage()

    # On remet la Dame dans la pioche après avoir utilisé son pouvoir
    if dame_carte in fosse:
        fosse.remove(dame_carte)
    elif dame_carte in pioche:
        pioche.remove(dame_carte)

    pioche.insert(0, dame_carte)  # Ajout de la Dame dans la pioche
    root.after(3000, lambda: masquer_temporairement(index))

def masquer_temporairement(index):
    visible_main[index] = False
    maj_affichage()

def cliquer_carte(index):
    global carte_en_attente, visible_main, selection_initiale

    if selection_initiale:
        visible_main[index] = True
        maj_affichage()
        root.after(5000, cacher_cartes)
        selection_initiale = False
        return

    if numero_joueur != tour_actuel or carte_en_attente is None:
        return

    envoi = {
        'type': 'remplacement',
        'index': index,
        'source': carte_en_attente
    }
    s.send(json.dumps(envoi).encode())
    carte_en_attente = None

def cacher_cartes():
    global visible_main
    visible_main = [False] * len(main_joueur)
    maj_affichage()

def piocher(source):
    global carte_en_attente
    if numero_joueur != tour_actuel or carte_en_attente is not None:
        return
    if source == "fosse" and not fosse:
        return
    carte_en_attente = source

def maj_donnees():
    global main_joueur, pioche, fosse, numero_joueur, tour_actuel, visible_main
    while True:
        try:
            data = s.recv(4096)
            if not data:
                break
            infos = json.loads(data.decode())
            main_joueur = infos['main']
            pioche = infos['pioche']
            fosse = infos['fosse']
            tour_actuel = infos['tour']
            numero_joueur = infos['joueur']
            if not visible_main or len(visible_main) != len(main_joueur):
                visible_main = [False] * len(main_joueur)
            maj_affichage()
        except:
            break

# --- Thread Réception données serveur ---
threading.Thread(target=maj_donnees, daemon=True).start()

# --- Boutons de jeu ---
tk.Button(main_frame, text="Prendre Pioche", command=lambda: piocher("pioche")).pack(pady=5)
tk.Button(main_frame, text="Prendre Fosse", command=lambda: piocher("fosse")).pack(pady=5)
tk.Label(main_frame, textvariable=etat_pioche).pack()
tk.Label(main_frame, textvariable=etat_fosse).pack()
tk.Label(main_frame, textvariable=etat_tour, font=("Arial", 12)).pack(pady=10)

# --- Lancement GUI ---
root.mainloop()
s.close()
