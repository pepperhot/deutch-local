# client.py

import socket
import json
import tkinter as tk
import threading

HOST = 'localhost'
PORT = 5000

game_start = False
pseudo_joueur = ""
main_joueur = []
pioche = []
fosse = []
visible_main = []
carte_en_attente = None
selection_initiale = True
numero_joueur = None
tour_actuel = None
action_effectuee = False
fin_deutch = False
joueurs = {}
red = ['♥', '♦']
negre = ['♠', '♣']
dernier_joueur = []
podium = {}
tour_actuel_pseudo = ""

root = tk.Tk()
root.title("🎮 DEUTCH - Jeu de Cartes")
root.configure(bg='#2C3E50')

etat_pioche = tk.StringVar()
etat_fosse = tk.StringVar()
etat_tour = tk.StringVar()

main_frame = tk.Frame(root)
main_frame.pack(padx=10, pady=10)

top_frame = tk.Frame(main_frame)
top_frame.pack(pady=(0, 10))

joueurs_frame_left = tk.Frame(main_frame)
joueurs_frame_left.pack(side='left', anchor='n', padx=10, pady=10)

joueurs_frame_right = tk.Frame(main_frame)
joueurs_frame_right.pack(side='right', anchor='n', padx=10, pady=10)

btn_frame = tk.Frame(main_frame)
btn_frame.pack()

label_pioche = tk.Label(top_frame, textvariable=etat_pioche)
label_fosse = tk.Label(top_frame, textvariable=etat_fosse)

btn_pioche = tk.Button(top_frame, text="↑piocher↑", command=lambda: piocher("pioche"))
btn_fosse = tk.Button(top_frame, text="↑piocher↑", command=lambda: piocher("fosse"))
btn_deutch = tk.Button(top_frame, text="deutch", command=lambda: deutch())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((HOST, PORT))


    def menu():
        global game_start

        # Nettoyer tous les widgets existants dans root
        for widget in root.winfo_children():
            widget.destroy()
        
        root.geometry("500x400")
        menu_frame = tk.Frame(root, bg='#2C3E50')
        menu_frame.pack(side="top", expand=True, fill='both')

        def start_game():
            global game_start, pseudo_joueur
            game_start = True
            pseudo_joueur = name_entry.get()
            if not pseudo_joueur:
                pseudo_joueur = "user"
            # Détruire tous les widgets du menu
            for widget in root.winfo_children():
                widget.destroy()
            
            # Recréer les frames de jeu
            global main_frame, top_frame, joueurs_frame_left, joueurs_frame_right, btn_frame
            global label_pioche, label_fosse, btn_pioche, btn_fosse, btn_deutch
            
            main_frame = tk.Frame(root, bg='#2C3E50')
            main_frame.pack(padx=10, pady=10, expand=True, fill='both')
            
            top_frame = tk.Frame(main_frame, bg='#34495E', relief='raised', bd=2)
            top_frame.pack(pady=(0, 15), padx=10, fill='x')
            
            joueurs_frame_left = tk.Frame(main_frame, bg='#34495E', relief='groove', bd=2)
            joueurs_frame_left.pack(side='left', anchor='n', padx=10, pady=10)
            
            joueurs_frame_right = tk.Frame(main_frame, bg='#34495E', relief='groove', bd=2)
            joueurs_frame_right.pack(side='right', anchor='n', padx=10, pady=10)
            
            btn_frame = tk.Frame(main_frame, bg='#2C3E50')
            btn_frame.pack(pady=15)
            
            label_pioche = tk.Label(top_frame, textvariable=etat_pioche, font=("Arial", 12, "bold"), bg='#34495E', fg='#ECF0F1')
            label_fosse = tk.Label(top_frame, textvariable=etat_fosse, font=("Arial", 12, "bold"), bg='#34495E', fg='#ECF0F1')
            
            btn_pioche = tk.Button(top_frame, text="🃏 Piocher", command=lambda: piocher("pioche"), 
                                  font=("Arial", 11, "bold"), bg='#3498DB', fg='white', activebackground='#2980B9', 
                                  relief='raised', padx=15, pady=8, cursor='hand2')
            btn_fosse = tk.Button(top_frame, text="♻️ Fosse", command=lambda: piocher("fosse"), 
                                 font=("Arial", 11, "bold"), bg='#9B59B6', fg='white', activebackground='#8E44AD', 
                                 relief='raised', padx=15, pady=8, cursor='hand2')
            btn_deutch = tk.Button(top_frame, text="🔔 DEUTCH", command=lambda: deutch(), 
                                  font=("Arial", 11, "bold"), bg='#E67E22', fg='white', activebackground='#D35400', 
                                  relief='raised', padx=15, pady=8, cursor='hand2')
            
            s.send(json.dumps({'type': 'pseudo', 'pseudo': pseudo_joueur}).encode())
            maj_affichage()

        label_menu = tk.Label(menu_frame, text="🎮 DEUTCH !", font=("Arial", 28, "bold"), bg='#2C3E50', fg='#ECF0F1')
        pseudo_label = tk.Label(menu_frame, text="Pseudo :", font=("Arial", 14), bg='#2C3E50', fg='#ECF0F1')
        name_entry = tk.Entry(menu_frame, font=("Arial", 14), width=20, bg='#ECF0F1', relief='flat', bd=2)
        start_button = tk.Button(menu_frame, text="🚀 Démarrer le jeu", command=start_game, font=("Arial", 14, "bold"), 
                                bg='#27AE60', fg='white', activebackground='#229954', relief='flat', padx=20, pady=10, cursor='hand2')
        quit_button = tk.Button(menu_frame, text="❌ Quitter", command=root.destroy, font=("Arial", 14), 
                               bg='#E74C3C', fg='white', activebackground='#C0392B', relief='flat', padx=20, pady=10, cursor='hand2')

        label_menu.grid(row=0, column=0, columnspan=2, pady=10)
        start_button.grid(row=1, column=0, columnspan=2, pady=10)
        pseudo_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        name_entry.grid(row=2, column=1, padx=5, pady=5)
        quit_button.grid(row=3, column=0, columnspan=2, pady=10)


    def maj_affichage():
        global main_joueur, visible_main, tour_actuel_pseudo
        root.geometry("800x500")

        if fin_deutch and numero_joueur not in dernier_joueur:
            dernier_joueur.append(numero_joueur)
        if not fin_deutch:
            # Nettoyer les widgets de main_frame
            for widget in main_frame.winfo_children():
                if isinstance(widget, tk.Label) or (isinstance(widget, tk.Button) and "Jeter la carte" in widget["text"]):
                    widget.destroy()
            
            for widget in btn_frame.winfo_children():
                widget.destroy()

            for widget in joueurs_frame_left.winfo_children():
                widget.destroy()
            
            for widget in joueurs_frame_right.winfo_children():
                widget.destroy()
            
            tour_label = tk.Label(main_frame, textvariable=etat_tour, font=("Arial", 14, "bold"), 
                                 bg='#34495E', fg='#F1C40F', relief='raised', bd=2, padx=20, pady=8)
            tour_label.pack(pady=10)

            label_pioche.grid(row=0, column=0, padx=10)
            label_fosse.grid(row=0, column=1, padx=10)

            btn_pioche.grid(row=1, column=0, padx=5, pady=5)
            btn_fosse.grid(row=1, column=1, padx=5, pady=5)

            btn_deutch.grid(row=1, column=2, padx=5)
            btn_deutch.config(state="normal" if len(joueurs) > 1 else "disabled")

            if joueurs:
                autres_joueurs = [(nom, main) for nom, main in joueurs.items() if nom != pseudo_joueur]
                moitie = len(autres_joueurs) // 2 + len(autres_joueurs) % 2
                ligne_left = 0
                ligne_right = 0

                for nom, main in autres_joueurs[:moitie]:
                    color = ("#E74C3C" if nom == tour_actuel_pseudo else "#ECF0F1") if not fin_deutch else "#2ECC71"
                    tk.Label(joueurs_frame_left, text=f"👤 {nom}", fg=color, font=("Arial", 12, "bold"), 
                            bg='#34495E', padx=10, pady=5).grid(row=ligne_left, column=0, sticky='w')
                    ligne_left += 1
                    for i, carte in enumerate(main):
                        tk.Button(joueurs_frame_left, text="🃏", font=("Arial", 14),
                                  command=lambda idx=i, joueur=nom: transition(idx, joueur), width=6,
                                  bg='#16A085', fg='white', activebackground='#138D75', 
                                  relief='raised', cursor='hand2').grid(
                            row=ligne_left, column=0, sticky='w', padx=10, pady=2)
                        ligne_left += 1

                for nom, main in autres_joueurs[moitie:]:
                    color = ("#E74C3C" if nom == tour_actuel_pseudo else "#ECF0F1") if not fin_deutch else "#2ECC71"
                    tk.Label(joueurs_frame_right, text=f"👤 {nom}", fg=color, font=("Arial", 12, "bold"), 
                            bg='#34495E', padx=10, pady=5).grid(row=ligne_right, column=0, sticky='e')
                    ligne_right += 1
                    for i, carte in enumerate(main):
                        tk.Button(joueurs_frame_right, text="🃏", font=("Arial", 14),
                                  command=lambda idx=i, joueur=nom: transition(idx, joueur), width=6,
                                  bg='#16A085', fg='white', activebackground='#138D75', 
                                  relief='raised', cursor='hand2').grid(
                            row=ligne_right, column=0, sticky='e', padx=10, pady=2)
                        ligne_right += 1

            for i, visible in enumerate(visible_main):
                if not visible:
                    tk.Button(btn_frame, text=f"🐑", command=lambda idx=i: mouton(idx), 
                             font=("Arial", 10), bg='#F39C12', fg='white', activebackground='#E67E22',
                             relief='raised', width=4, cursor='hand2').grid(row=0, column=i, pady=5, padx=2)

            for i, carte in enumerate(main_joueur):
                texte = carte if visible_main[i] else "🎴"
                # Couleur selon la carte
                if visible_main[i] and len(carte) > 0:
                    couleur_carte = '#E74C3C' if carte[-1] in ['♥', '♦'] else '#2C3E50'
                else:
                    couleur_carte = '#1ABC9C'
                tk.Button(btn_frame, text=texte, font=("Arial", 14, "bold"), width=6,
                          command=lambda idx=i: cliquer_carte(idx),
                          bg=couleur_carte, fg='white', activebackground='#16A085',
                          relief='raised', padx=5, pady=10, cursor='hand2').grid(row=1, column=i, padx=3, pady=5)

            etat_pioche.set("Pioche : ❓")
            etat_fosse.set(f"Fosse : {fosse[-1]}")

            if len(pioche) == 1:
                s.send(json.dumps({'type': 'vide', 'carte': fosse[-1]}).encode())

            if numero_joueur is not None and tour_actuel is not None:
                etat_tour.set("À vous de jouer" if numero_joueur == tour_actuel else "En attente du tour")

            dame_carte = None

            if carte_en_attente == "pioche" and pioche and pioche[0] in ["D♠", "D♥", "D♦", "D♣"]:
                dame_carte = pioche[0]
            elif carte_en_attente == "fosse" and fosse and fosse[-1] in ["D♠", "D♥", "D♦", "D♣"]:
                dame_carte = fosse[-1]
            if dame_carte:
                for i, visible in enumerate(visible_main):
                    if not visible:
                        tk.Button(btn_frame, text=f"👁 Voir",
                                  command=lambda idx=i, dc=dame_carte: utiliser_pouvoir_dame(idx, dc),
                                  font=("Arial", 9, "bold"), bg='#9B59B6', fg='white', 
                                  activebackground='#8E44AD', relief='raised', width=6, cursor='hand2').grid(row=2,
                                                                                                            column=i,
                                                                                                            pady=5, padx=2)

            if numero_joueur == tour_actuel:
                tk.Button(main_frame, text="🗑️ Jeter la carte", command=jeter_carte,
                         font=("Arial", 12, "bold"), bg='#E74C3C', fg='white', 
                         activebackground='#C0392B', relief='raised', padx=20, pady=10, 
                         cursor='hand2').pack(pady=10)


    def mouton(idx):
        # Extraire la valeur de la carte (tout sauf le dernier caractère qui est la couleur)
        valeur_joueur = main_joueur[idx][:-1]
        valeur_fosse = fosse[-1][:-1]
        
        if valeur_joueur == valeur_fosse:
            envoi = {'type': 'mouton', 'index': idx, 'carte': main_joueur[idx], 'reussi': True}
        else:
            envoi = {'type': 'mouton', 'index': idx, 'carte': None, 'reussi': False}
        s.send(json.dumps(envoi).encode())


    def remplacer_carte(index):
        global carte_en_attente
        envoi = {'type': 'action', 'index': index, 'source': carte_en_attente}
        s.send(json.dumps(envoi).encode())
        carte_en_attente = None


    def jeter_carte():
        global carte_en_attente, action_effectuee
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
        envoi = {'type': 'jeter', 'source': carte_en_attente, 'carte': carte_jetee}
        s.send(json.dumps(envoi).encode())
        carte_en_attente = None
        action_effectuee = True
        root.after(2000, maj_affichage)


    def utiliser_pouvoir_dame(index, dame_carte):
        global visible_main, carte_en_attente, action_effectuee

        visible_main[index] = True
        action_effectuee = True
        maj_affichage()
        root.after(3000, lambda: masquer_temporairement(index))
        envoi = {'type': 'dame', 'source': dame_carte, 'carte': dame_carte}
        s.send(json.dumps(envoi).encode())
        carte_en_attente = None


    def transition(idx_victime, joueur_victime):
        global carte_en_attente

        valet_carte = ""
        if pioche and pioche[0].startswith("V") and pioche[0]:
            valet_carte = pioche[0]
        elif fosse and fosse[-1].startswith("V") and fosse[-1]:
            valet_carte = fosse[-1]

        ten_carte = ""
        if pioche and pioche[0][:-1] == "10" and pioche[0][-1] in red and pioche[0]:
            ten_carte = pioche[0]
        elif fosse and fosse[-1][:-1] == "10" and fosse[-1][-1] in red and fosse[-1]:
            ten_carte = fosse[-1]

        if not valet_carte and not ten_carte:
            return

        if valet_carte:
            print("valet")
            carte_en_attente = valet_carte

            def utiliser_pouvoir_valet(idx_attaquant):
                global carte_en_attente
                envoi = {
                    'type': 'valet',
                    'carte': valet_carte,
                    'victime': joueur_victime,
                    'index_victime': idx_victime,
                    'index_attaquant': idx_attaquant,
                    'carte_attaquant': main_joueur[idx_attaquant]
                }
                s.send(json.dumps(envoi).encode())
                carte_en_attente = None
                maj_affichage()

            # Nettoyer les boutons existants de la ligne 2
            for widget in btn_frame.grid_slaves(row=2):
                widget.destroy()
            
            for i, visible in enumerate(visible_main):
                tk.Button(btn_frame, text="🔄", command=lambda idx=i: utiliser_pouvoir_valet(idx),
                         font=("Arial", 10, "bold"), bg='#E67E22', fg='white', 
                         activebackground='#D35400', relief='raised', width=4, cursor='hand2').grid(row=2, column=i,
                                                                                                    pady=5, padx=2)

        if ten_carte:
            print("ten")
            carte_en_attente = ten_carte
            envoi = {
                'type': "red_ten",
                'carte': ten_carte,
                'victime': joueur_victime,
                'index_victime': idx_victime
            }
            s.send(json.dumps(envoi).encode())
            carte_en_attente = None
            maj_affichage()


    def masquer_temporairement(index):
        visible_main[index] = False
        maj_affichage()


    def cliquer_carte(index):
        global carte_en_attente, visible_main, selection_initiale, action_effectuee

        if selection_initiale:
            visible_main[index] = True
            root.after(5000, cacher_cartes)
            maj_affichage()
            selection_initiale = False
            return

        if numero_joueur == tour_actuel and carte_en_attente is None and not action_effectuee:
            visible_main[index] = True
            action_effectuee = True
            maj_affichage()
            return

        if numero_joueur != tour_actuel or carte_en_attente is None:
            return

        envoi = {'type': 'action', 'index': index, 'source': carte_en_attente}
        s.send(json.dumps(envoi).encode())
        carte_en_attente = None
        action_effectuee = True


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
        maj_affichage()
        if source == "pioche" and pioche:
            carte = pioche[0]
            if carte_en_attente:
                etat_pioche.set(f"Pioche : {carte}")


    def deutch():
        global fin_deutch
        fin_deutch = True
        envoi = {'type': 'deutch',
                 'deutch_man': numero_joueur}
        s.send(json.dumps(envoi).encode())


    def afficher_les_resultats(podium):
        largeur = root.winfo_width() or 800
        hauteur = root.winfo_height() or 600
        canvas = tk.Canvas(root, width=largeur, height=hauteur, highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        canvas.create_rectangle(0, 0, largeur, hauteur, fill='gray', stipple='gray25', outline='')
        canvas.create_text(largeur // 2, 50, text="🏆 Fin de la partie ! 🏆", fill="black",
                           font=("Helvetica", 32, "bold"))
        for i, (nom, score) in enumerate(podium.items(), start=1):
            print(nom[-1], numero_joueur, nom[-1] == numero_joueur)
            canvas.create_text(largeur // 2, 100 + i * 30,
                               text=f"{i}. {nom} - {score} pts {'←you' if nom == pseudo_joueur else ''}", fill="black",
                               font=("Helvetica", 16))
        bouton_quitter = tk.Button(canvas, text="Quitter", font=("Helvetica", 14), command=root.destroy)
        canvas.create_window(largeur // 2, hauteur - 50, window=bouton_quitter)


    def maj_donnees():
        global main_joueur, pioche, fosse, tour_actuel, numero_joueur, visible_main, joueurs, podium, tour_actuel_pseudo, action_effectuee
        ancien_tour = None
        while True:
            try:
                data = s.recv(8192)
                if not data:
                    break
                try:
                    infos = json.loads(data.decode())
                except json.JSONDecodeError as je:
                    print(f"Erreur de décodage JSON : {je}")
                    continue
                main_joueur = infos['main']
                pioche = infos['pioche']
                fosse = infos['fosse']
                ancien_tour = tour_actuel
                tour_actuel = infos['tour']
                numero_joueur = infos['joueur']
                visible_main = visible_main[:len(main_joueur)]
                joueurs = infos['joueurs']
                podium = infos['podium']
                tour_actuel_pseudo = infos.get('tour_pseudo')
                if podium or main_joueur == []:
                    afficher_les_resultats(podium)
                while len(visible_main) < len(main_joueur):
                    visible_main.append(False)
                if numero_joueur == infos['joueur'] and tour_actuel != ancien_tour:
                    action_effectuee = False
                if game_start:
                    maj_affichage()
                else:
                    menu()
            except Exception as e:
                print(f"Erreur lors de la réception des données : {e}")
                break


    threading.Thread(target=maj_donnees, daemon=True).start()
    root.mainloop()
    s.close()

except ConnectionRefusedError:
    print("Erreur de connexion au serveur.")
    s.close()
    root.destroy()