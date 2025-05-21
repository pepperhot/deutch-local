#server.py

import socket
import threading
import json
import random
import time

HOST = '0.0.0.0'
PORT = 5000

cartes = [f"{val}{coul}" for coul in ['♠', '♥', '♦', '♣'] for val in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']]
random.shuffle(cartes)

nb_cartes_joueur = 5
mains = {}
clients = []
pioche = cartes[:-1]
fosse = [cartes[-1]]
tour_actuel = 0
total_mains = {}
joueur_socket = {}
dame_used = []
valet_used = []
ten_used = []
deutch = False
dernier_joueur = []
classement = {}
lock = threading.Lock()


def envoyer_etat():
    
    for i, (client, addr) in enumerate(clients):
        joueurs_info = {f"Joueur {i}": mains[addr] for i, (client, addr) in enumerate(clients)}
        podium = dict(sorted(classement.items(), key=lambda item: item[1])) if len(dernier_joueur) == len(classement) else None
        infos = {
            'main': mains[addr],
            'pioche': pioche,
            'fosse': fosse,
            'tour': tour_actuel,
            'joueur': i,
            'joueurs': joueurs_info,
            'fin' : deutch,
            'podium' : podium
        }
        try:
            client.send(json.dumps(infos).encode())
        except:
            continue

def afficher_etat_serveur():
    print("\n=== ÉTAT ACTUEL DU JEU ===")
    print(f"Carte de départ dans la fosse: {fosse[0] if fosse else 'aucune'}")
    print(f"Pioche: {', '.join(pioche)}")
    print(f"Fosse: {', '.join(fosse)}")
    print(f"Tour actuel: Joueur {tour_actuel}")
    for addr in mains:
        print(f"Main de {addr}: {mains[addr]}")
    print("==========================\n")

def gerer_client(client, addr, joueur_id):
    global tour_actuel
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            message = json.loads(data.decode())

            if message['type'] == 'vide':
                carte_fosse = message.get('carte')
                if carte_fosse and carte_fosse in fosse:
                    fosse.remove(carte_fosse)
                    random.shuffle(fosse)
                    pioche.extend(fosse)
                    fosse.clear()
                    fosse.append(carte_fosse)

            elif message['type'] == 'remplacement':
                index = message['index']
                source = message['source']
                with lock:
                    if joueur_id == tour_actuel:
                        if source == 'pioche' and pioche:
                            carte = pioche.pop(0)
                        elif source == 'fosse' and fosse:
                            carte = fosse.pop()
                        else:
                            continue
                        ancienne = mains[addr][index]
                        mains[addr][index] = carte
                        fosse.append(ancienne)
                        tour_actuel = (tour_actuel + 1) % len(clients)
                        envoyer_etat()
                        afficher_etat_serveur()

            elif message['type'] == 'jeter':
                source = message['source']
                carte = message.get('carte')
                with lock:
                    if joueur_id == tour_actuel:
                        if source == 'pioche' and pioche:
                            carte = pioche.pop(0)
                            fosse.append(carte)
                        elif source == 'fosse' and fosse:
                            carte = fosse.pop()
                            fosse.append(carte)
                        else:
                            return
                        tour_actuel = (tour_actuel + 1) % len(clients)
                        envoyer_etat()
                        afficher_etat_serveur()

            elif message['type'] == 'dame':
                source = message['source']
                carte = message.get('carte')
                if not carte or carte in dame_used:
                    continue
                with lock:
                    if joueur_id == tour_actuel:
                        if carte.startswith('D'):
                            dame_used.append(carte)
                            fosse.append(carte)
                            tour_actuel = (tour_actuel + 1) % len(clients)
                            envoyer_etat()
                            afficher_etat_serveur()

            elif message['type'] == 'valet':
                carte = message.get('carte')
                victime = message['victime']
                idx_victime = message['index_victime']
                idx_attaquant = message['index_attaquant']
                carte_attaquant = message.get('carte_attaquant')
                if not carte or carte in valet_used:
                    continue
                with lock:
                    if joueur_id == tour_actuel:
                        valet_used.append(carte)
                        mains[addr].remove(carte_attaquant)
                        carte_victime = mains[joueur_socket[victime]][idx_victime]
                        mains[joueur_socket[victime]].remove(carte_victime)
                        mains[addr].insert(idx_attaquant, carte_victime)
                        mains[joueur_socket[victime]].insert(idx_victime, carte_attaquant)
                        if carte not in fosse:
                            fosse.append(carte)
                        else:
                            continue
                        tour_actuel = (tour_actuel + 1) % len(clients)
                        envoyer_etat()
                        afficher_etat_serveur()

            elif message['type'] == 'red_ten':
                carte = message['carte']
                idx_victime = message['index_victime']
                victime = message['victime']
                if not carte or carte in ten_used:
                    continue
                with lock:
                    ten_used.append(carte)
                    victime_main = mains[joueur_socket[victime]]
                    carte_victime = victime_main.pop(idx_victime)
                    victime_main.insert(idx_victime, carte)
                    if carte_victime not in fosse:
                        fosse.append(carte_victime)
                    else:return
                    tour_actuel = (tour_actuel + 1) % len(clients)
                    envoyer_etat()
                    afficher_etat_serveur()

            elif message['type'] == 'mouton':
                index = message['index']
                carte = message.get('carte')
                with lock:
                    if carte:
                        carte = mains[addr].pop(index)
                        fosse.append(carte)
                    else:
                        if len(pioche) >= 2:
                            mains[addr].append(pioche.pop(0))
                            mains[addr].append(pioche.pop(0))
                    tour_actuel = (tour_actuel + 1) % len(clients)
                    envoyer_etat()
                    afficher_etat_serveur()

            elif message['type'] == 'deutch':
                deutch_man = message['deutch_man']
                if deutch_man not in dernier_joueur:
                    dernier_joueur.append(deutch_man)

                if len(dernier_joueur) == len(clients):
                    global deutch
                    deutch = True

                    def valeur_carte(c):
                        val = c[:-1]
                        if val in ['V', 'D']:
                            return 10
                        elif val == 'A':
                            return 1
                        elif c in ['R♥', 'R♦']:
                             return 0
                        elif c in ['R♠', 'R♣']:
                            return 90
                        else:
                            return int(val)

                    for i, (client, addr) in enumerate(clients):
                        main = mains[addr]
                        score = sum(valeur_carte(carte) for carte in main)
                        classement[f"Joueur {i}"] = score

                tour_actuel = (tour_actuel + 1) % len(clients)
                envoyer_etat()
                afficher_etat_serveur()

        except:
            break
    client.close()

# --- Serveur principal ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print(f"Serveur lancé sur {HOST}:{PORT}, en attente de connexions...")

def accepter_connexions():
    while True:
        client, addr = s.accept()
        print(f"[+] Nouveau joueur connecté depuis {addr}")
        with lock:
            main = [pioche.pop(0) for _ in range(nb_cartes_joueur)]
            mains[addr] = main
            clients.append((client, addr))
            envoyer_etat()
            afficher_etat_serveur()
            joueur_id = len(clients) - 1
            joueur_socket[f"Joueur {joueur_id}"] = addr
        threading.Thread(target=gerer_client, args=(client, addr, joueur_id), daemon=True).start()

accepter_connexions()