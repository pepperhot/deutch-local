import socket
import json
import tkinter as tk
import threading

HOST = 'localhost'
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

root = tk.Tk()
root.title("Jeu de mémoire - Client")

etat_pioche = tk.StringVar()
etat_fosse = tk.StringVar()
etat_tour = tk.StringVar()

# Conteneur principal
main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

# Frame du haut : pioche, fosse, boutons
top_frame = tk.Frame(main_frame)
top_frame.pack(pady=(0, 10))

# Labels Pioche et Fosse
tk.Label(top_frame, textvariable=etat_pioche).grid(row=0, column=0, padx=10)
tk.Label(top_frame, textvariable=etat_fosse).grid(row=0, column=1, padx=10)

# Boutons côte à côte
btn_pioche = tk.Button(top_frame, text="Prendre Pioche", command=lambda: piocher("pioche"))
btn_pioche.grid(row=1, column=0, padx=5, pady=5)

btn_fosse = tk.Button(top_frame, text="Prendre Fosse", command=lambda: piocher("fosse"))
btn_fosse.grid(row=1, column=1, padx=5, pady=5)

# Label pour le tour
tk.Label(main_frame, textvariable=etat_tour, font=("Arial", 12)).pack()

# Frame pour les cartes du joueur
btn_frame = tk.Frame(main_frame)
btn_frame.pack()

# --- Socket ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))

    def maj_affichage():
        global main_joueur, visible_main

        for widget in btn_frame.winfo_children():
            widget.destroy()

        for i, carte in enumerate(main_joueur):
            texte = carte if visible_main[i] else "❓"
            btn = tk.Button(btn_frame, text=texte, font=("Arial", 12), width=6,
                            command=lambda idx=i: cliquer_carte(idx))
            btn.grid(row=0, column=i, padx=5)

        etat_pioche.set("Pioche : ❓")
        etat_fosse.set(f"Fosse : {fosse[-1] if fosse else 'vide'}")

        if numero_joueur is not None and tour_actuel is not None:
            etat_tour.set("À vous de jouer" if numero_joueur == tour_actuel else "En attente du tour")

        if numero_joueur == tour_actuel and carte_en_attente is None:
            dame_carte = ""
            if pioche and pioche[0].startswith("D") and pioche[0] not in dame_used:
                dame_carte = pioche[0]
                print("Dame de pioche :", dame_carte)
            elif fosse and fosse[-1].startswith("D") and fosse[-1] not in dame_used:
                dame_carte = fosse[-1]
                print("Dame de fosse :", dame_carte)

            if dame_carte:
                for i, visible in enumerate(visible_main):
                    if not visible:
                        btn = tk.Button(btn_frame, text=f"👁 Voir {i + 1}",
                                        command=lambda idx=i, dc=dame_carte: utiliser_pouvoir_dame(idx, dc))
                        btn.grid(row=1, column=i, pady=5)
            if numero_joueur == tour_actuel and carte_en_attente is not None:
                action_frame = tk.Frame(main_frame)
                action_frame.pack(pady=5)
                tk.Button(action_frame, text="🗑 Jeter la carte", command=jeter_carte).pack()


    def remplacer_carte(index):
        global carte_en_attente
        s.send(json.dumps({'type': 'remplacement', 'index': index, 'source': carte_en_attente}).encode())
        carte_en_attente = None

    def jeter_carte():
        global carte_en_attente

        if numero_joueur != tour_actuel or carte_en_attente is None:
            return
        if carte_en_attente == 'pioche' and pioche:
            carte_jetee = pioche[0]
            etat_pioche.set(f"Jetée : {carte_jetee}")
        elif carte_en_attente == 'fosse' and fosse:
            carte_jetee = fosse[-1]
            etat_fosse.set(f"Jetée : {carte_jetee}")
        else:
            return
        s.send(json.dumps({'type': 'jeter', 'source': carte_en_attente, 'carte': carte_jetee
        }).encode())
        carte_en_attente = None
        root.after(2000, maj_affichage)

    def utiliser_pouvoir_dame(index, dame_carte):
        global dame_used, visible_main, carte_en_attente

        visible_main[index] = True
        dame_used.append(dame_carte)
        maj_affichage()
        root.after(3000, lambda: masquer_temporairement(index))
        s.send(json.dumps({'type': 'dame', 'source': dame_carte, 'carte': dame_carte}).encode())
        carte_en_attente = None


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

        envoi = {'type': 'remplacement', 'index': index, 'source': carte_en_attente}
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


        # Affichage temporaire de la carte de pioche
        if source == "pioche" and pioche:
            etat_pioche.set(f"Pioche : {pioche[0]}")
            root.after(3000, lambda: etat_pioche.set("Pioche : ❓"))

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

    threading.Thread(target=maj_donnees, daemon=True).start()
    root.mainloop()
    s.close()

except ConnectionRefusedError:
    print("Erreur de connexion au serveur.")
    s.close()
    root.destroy()
