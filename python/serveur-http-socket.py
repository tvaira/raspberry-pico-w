import machine
import time
import network
import socket
import json

# Paramètres de connexion WiFi
ssid = 'SSID'
password = 'PASSWORD'

# Les réponses HTTP
reponseHTTPOk = """HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: {length}
Server: MicroPython

{json}"""

reponseHTTPErreur = b"HTTP/1.1 404 File not found\r\n\r\n"

# L'interface WiFi (client d'un point d'accès WiFi)
wlan = network.WLAN(network.STA_IF)

# Les fonctions
def initialiserWiFi():
   wlan.active(True)
   wlan.config(pm = 0xa11140)

def connecterWiFi(ssid, password):
   wlan.connect(ssid, password)
   # Connexion
   nbTentatives = 10
   while nbTentatives > 0:
      if wlan.status() < 0 or wlan.status() >= 3:
         break
      nbTentatives -= 1
      print('Attente de connexion...')
      time.sleep(1)

   # Connecté ?
   if wlan.status() != 3:
      raise RuntimeError('Erreur de connexion')
   else:
      print('SSID = ' + str(wlan.config('essid')))
      infos = wlan.ifconfig()
      adresseIP = infos[0]
      print('Adresse IP = ' + adresseIP)

def deconnecterWiFi():
   # Déconnexion
   wlan.disconnect()

def creerSocketEcoute():
   ADRESSE_ECOUTE = '0.0.0.0' # toutes les interfaces
   PORT_ECOUTE = 80
   pointCommunicationLocal = socket.getaddrinfo(ADRESSE_ECOUTE, PORT_ECOUTE)[0][-1]
   s = socket.socket()
   s.bind(pointCommunicationLocal)
   s.listen(1)
   print('Ecoute serveur sur', pointCommunicationLocal)
   return s

def getTemperature():
   tensionPICO = 3.3
   quantumCAN = tensionPICO / 65535
   capteurTemperature = machine.ADC(machine.ADC.CORE_TEMP)
   valeurCAN = capteurTemperature.read_u16()
   tensionCAN = valeurCAN * quantumCAN
   temperature = 27 - (tensionCAN - 0.706)/0.001721
   return temperature

# Le serveur HTTP
initialiserWiFi()

connecterWiFi(ssid, password)

socketEcoute = creerSocketEcoute()

# c'est un serveur ;)
while True:
   try:
      socketDialogue, pointCommunicationDistant = socketEcoute.accept()
      print('Client connecté : ', pointCommunicationDistant)
      # Voir aussi : makefile()
      # https://docs.micropython.org/en/v1.20.0/library/socket.html
      # Reception des données
      requete = socketDialogue.recv(1024)
      print("Requete recue : " + str(requete))
      requete = str(requete)
      if(requete.find('/temperature') != -1):
         donneesJSON = json.dumps({'temperature': str(getTemperature())})
         reponse = reponseHTTPOk.format(length=len(donneesJSON), json=donneesJSON)
         print("Reponse envoyee : " + str(reponse))
         socketDialogue.send(reponse)
         socketDialogue.close()
      else:
         print("Reponse envoyee : " + str(reponseHTTPErreur))
         socketDialogue.send(reponseHTTPErreur)
         socketDialogue.close()
      print('Deconnexion : ', pointCommunicationDistant)
   except OSError as e:
      socketDialogue.close()
      print('Deconnexion : ', pointCommunicationDistant)

deconnecterWiFi()
