import socket
import threading
import json
import random
import time

HOST = '0.0.0.0'
PORT = 5000

# Création du paquet de cartes
cartes = [f"{val}{coul}" for coul in ['♠', '♥', '♦', '♣'] for val in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']]
random.shuffle(cartes)

nb_cartes_joueur = 5
mains = {}
clients = []
pioche = cartes[:-1]  # Toutes sauf une
fosse = [cartes[-1]]  # Une carte au départ dans la fosse
tour_actuel = 0
lock = threading.Lock()

def envoyer_etat():
    for i, (client, addr) in enumerate(clients):
        infos = {
            'main': mains[addr],
            'pioche': pioche,
            'fosse': fosse,
            'tour': tour_actuel,
            'joueur': i
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

            if message['type'] == 'remplacement':
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
                            print(f"Joueur {joueur_id} a jeté la carte {carte} de la pioche.")
                        elif source == 'fosse' and fosse:
                            carte = fosse.pop()
                            fosse.append(carte)
                            print(f"Joueur {joueur_id} a rejeté la carte {carte} de la fosse.")
                        else:
                            print(f"Source invalide ou vide pour joueur {joueur_id}: {source}")
                            return
                        tour_actuel = (tour_actuel + 1) % len(clients)
                        envoyer_etat()
                        afficher_etat_serveur()


            elif message['type'] == 'dame':
                source = message['source']
                carte = message.get('carte')
                if not carte:
                    print("Erreur : carte non spécifiée dans le message dame.")
                    continue

                print(f"la dame {carte}")
                with lock:
                    if joueur_id == tour_actuel:
                        if carte.startswith('D'):
                            fosse.append(carte)
                            tour_actuel = (tour_actuel + 1) % len(clients)
                            envoyer_etat()
                            afficher_etat_serveur()
                    else:
                        print(f"Le joueur {addr} a essayé de jouer une carte alors ce n'est pas son tour.")

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
        threading.Thread(target=gerer_client, args=(client, addr, joueur_id), daemon=True).start()

accepter_connexions()
