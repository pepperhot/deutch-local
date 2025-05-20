mon_dict = {'aba': 1, 'ana': 2, 'ava': 3, 'apa': 0}

dict_trie_par_valeur = dict(sorted(mon_dict.items(), key=lambda item: item[1]))

print(dict_trie_par_valeur)
