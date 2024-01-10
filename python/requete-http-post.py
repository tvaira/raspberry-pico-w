import time
import network
import json
import urequests as requests

ssid = 'SSID'
password = 'PASSWORD'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

def connecterWiFi():
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

connecterWiFi()

donneesJSON = json.dumps({'titre': 'hello world'})
# Free fake API for testing and prototyping
url = 'http://jsonplaceholder.typicode.com/posts'
print("Requete URL : " + url)
print("Donnees JSON : " + donneesJSON)
reponse = requests.post(url, data=donneesJSON)
print("Code retour = " + str(reponse.status_code))
print("Message = " + str(reponse.reason))
print("JSON : " + str(reponse.json()))

deconnecterWiFi()
