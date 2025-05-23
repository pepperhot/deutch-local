import socket

s = socket.socket()
s.bind(("localhost", 5000))
s.listen(1)
print("Serveur prêt")
client, addr = s.accept()
print("Client connecté")

data = client.recv(1024)
print("Reçu :", data.decode())
client.close()
