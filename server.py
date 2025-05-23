import socket
import threading
import json
import random

HOST = '0.0.0.0'
PORT = 5000

# Préparer le paquet de cartes
cartes = [f"{val}{coul}" for coul in ['♠', '♥', '♦', '♣']
          for val in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'V', 'D', 'R', 'A']]
random.shuffle(cartes)

# Initialisation des variables globales
nb_cartes_joueur = 5
clients = []  # Liste de tuples (client_socket, client_address)
mains = {}  # addr -> main du joueur
pioche = cartes[:-1]
fosse = [cartes[-1]]
tour_actuel = 0
classement = {}
pseudos = {}  # addr -> pseudo
dernier_joueur = []

# Cartes spéciales déjà utilisées
dame_used = []
valet_used = []
ten_used = []

deutch = False

lock = threading.Lock()


def envoyer_etat():
    with lock:
        for i, (client, addr) in enumerate(clients):
            joueurs_info = {pseudos.get(a, f"Joueur {j}"): mains[a] for j, (c, a) in enumerate(clients)}
            podium = dict(sorted(classement.items(), key=lambda item: item[1])) if deutch else None
            infos = {
                'main': mains[addr],
                'pioche': pioche,
                'fosse': fosse,
                'tour': tour_actuel,
                'joueur': i,
                'joueurs': joueurs_info,
                'fin': deutch,
                'podium': podium
            }
            try:
                client.send(json.dumps(infos).encode())
            except Exception as e:
                print(f"[ERREUR] Impossible d'envoyer l'état à {addr} : {e}")


def afficher_etat_serveur():
    with lock:
        print("\n=== ÉTAT ACTUEL DU JEU ===")
        print(f"Carte de départ dans la fosse: {fosse[0] if fosse else 'aucune'}")
        print(f"Pioche: {len(pioche)} cartes")
        print(f"Fosse: {', '.join(fosse)}")
        print(f"Tour actuel: Joueur {tour_actuel}")
        for addr in mains:
            print(f"Main de {pseudos[addr]} ({addr}): {mains[addr]}")
        print("==========================\n")


def valeur_carte(c):
    val = c[:-1]
    if val == 'A':
        return 1
    if val in ['V', 'D']:
        return 10
    if c in ['R♥', 'R♦']:
        return 0
    if c in ['R♠', 'R♣']:
        return 90
    return int(val)


def gerer_client(client, addr, joueur_id):
    global tour_actuel, deutch
    while True:
        try:
            data = client.recv(4096)
            if not data:
                break
            message = json.loads(data.decode())
            mtype = message.get('type')

            with lock:
                if mtype == 'pseudo':
                    pseudos[addr] = message['pseudo']
                elif mtype == 'vide':
                    carte_fosse = message.get('carte')
                    if carte_fosse in fosse:
                        fosse.remove(carte_fosse)
                        random.shuffle(fosse)
                        pioche.extend(fosse)
                        fosse.clear()
                        fosse.append(carte_fosse)
                elif mtype == 'action':
                    if joueur_id == tour_actuel:
                        index = message['index']
                        source = message['source']
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
                elif mtype == 'jeter':
                    if joueur_id == tour_actuel:
                        source = message['source']
                        if source == 'pioche' and pioche:
                            carte = pioche.pop(0)
                        elif source == 'fosse' and fosse:
                            carte = fosse.pop()
                        else:
                            continue
                        fosse.append(carte)
                        tour_actuel = (tour_actuel + 1) % len(clients)
                elif mtype == 'dame':
                    carte = message['carte']
                    if carte and carte not in dame_used:
                        dame_used.append(carte)
                        if carte not in fosse:
                            fosse.append(carte)
                        if carte in pioche:
                            pioche.remove(carte)
                        tour_actuel = (tour_actuel + 1) % len(clients)
                elif mtype == 'valet':
                    carte = message['carte']
                    victime = message['victime']
                    carte_victime = mains_by_pseudo(victime)[message['index_victime']]
                    carte_attaquant = message['carte_attaquant']
                    if carte and carte not in valet_used:
                        valet_used.append(carte)
                        mains[addr].pop(message['index_attaquant'])
                        mains_by_pseudo(victime).remove(carte_victime)
                        mains[addr].insert(message['index_attaquant'], carte_victime)
                        mains_by_pseudo(victime).insert(message['index_victime'], carte_attaquant)
                        if carte not in fosse:
                            fosse.append(carte)
                        if carte in pioche:
                            pioche.remove(carte)
                        tour_actuel = (tour_actuel + 1) % len(clients)
                elif mtype == 'red_ten':
                    carte = message['carte']
                    victime = message['victime']
                    idx_victime = message['index_victime']
                    if carte and carte not in ten_used:
                        ten_used.append(carte)
                        victime_main = mains_by_pseudo(victime)
                        ancienne = victime_main.pop(idx_victime)
                        victime_main.insert(idx_victime, carte)
                        fosse.append(ancienne)
                        if carte in pioche:
                            pioche.remove(carte)
                        elif carte in fosse:
                            fosse.remove(carte)
                        tour_actuel = (tour_actuel + 1) % len(clients)
                elif mtype == 'mouton':
                    index = message['index']
                    if 'carte' in message:
                        carte = mains[addr].pop(index)
                        fosse.append(carte)
                    else:
                        if len(pioche) >= 2:
                            mains[addr].extend([pioche.pop(0), pioche.pop(0)])
                    tour_actuel = (tour_actuel + 1) % len(clients)
                elif mtype == 'deutch':
                    joueur = message['deutch_man']
                    if joueur not in dernier_joueur:
                        dernier_joueur.append(joueur)
                    if len(dernier_joueur) == len(clients):
                        deutch = True
                        for i, (cli, a) in enumerate(clients):
                            score = sum(valeur_carte(c) for c in mains[a])
                            classement[pseudos[a]] = score
                    tour_actuel = (tour_actuel + 1) % len(clients)

            envoyer_etat()
            afficher_etat_serveur()

        except Exception as e:
            print(f"Erreur lors de la réception du message de {addr} : {e}")
            break
    client.close()


def mains_by_pseudo(pseudo):
    for addr, name in pseudos.items():
        if name == pseudo:
            return mains[addr]
    return []


def accepter_connexions():
    while True:
        client, addr = s.accept()
        print(f"[+] Connexion de {addr}")
        with lock:
            main = [pioche.pop(0) for _ in range(nb_cartes_joueur)]
            mains[addr] = main
            clients.append((client, addr))
            joueur_id = len(clients) - 1
            pseudos[addr] = f"Joueur {joueur_id}"
        threading.Thread(target=gerer_client, args=(client, addr, joueur_id), daemon=True).start()
        envoyer_etat()
        afficher_etat_serveur()


# Démarrage du serveur
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
print(f"Serveur en attente sur {HOST}:{PORT}")
accepter_connexions()
