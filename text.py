dict = {'Joueur 1': 25, 'Joueur 0': 43}
for i, (nom, score) in enumerate(dict.items(), start=1):
    texte = f"{i}. {nom} - {score} pts"
    print(texte)