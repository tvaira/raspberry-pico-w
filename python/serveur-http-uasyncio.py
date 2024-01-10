import machine
import time
import network
import socket
import json
import uasyncio as asyncio

# Basé sur https://gist.github.com/aallan/3d45a062f26bc425b22a17ec9c81e3b6

# Paramètres de connexion WiFi
ssid = 'SSID'
password = 'PASSWORD'

# La led embarquée
led = machine.Pin("LED", machine.Pin.OUT)

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

def getTemperature():
   tensionPICO = 3.3
   quantumCAN = tensionPICO / 65535
   capteurTemperature = machine.ADC(machine.ADC.CORE_TEMP)
   valeurCAN = capteurTemperature.read_u16()
   tensionCAN = valeurCAN * quantumCAN
   temperature = 27 - (tensionCAN - 0.706)/0.001721
   return temperature

# Le serveur HTTP
ADRESSE_ECOUTE = '0.0.0.0' # toutes les interfaces
PORT_ECOUTE = 80

async def demarrerServeurHTTP(reader, writer):
   print('Client connecté')
   requete = await reader.readline()
   print("Requete recue : " + str(requete))
   # Ignorer les en-têtes HTTP
   while await reader.readline() != b"\r\n":
      pass
   requete = str(requete)
   if(requete.find('/temperature') != -1):
      donneesJSON = json.dumps({'temperature': str(getTemperature())})
      reponse = reponseHTTPOk.format(length=len(donneesJSON), json=donneesJSON)
      print("Reponse envoyee : " + str(reponse))
      writer.write(reponse)
      await writer.drain()
      await writer.wait_closed()
   else:
      print("Reponse envoyee : " + str(reponseHTTPErreur))
      writer.write(reponseHTTPErreur)
      await writer.drain()
      await writer.wait_closed()
   print('Deconnexion')

async def main():
   initialiserWiFi()
   connecterWiFi(ssid, password)
   asyncio.create_task(asyncio.start_server(demarrerServeurHTTP, ADRESSE_ECOUTE, PORT_ECOUTE))
   while True:
      led.on()
      await asyncio.sleep(0.25)
      led.off()
      await asyncio.sleep(5)

try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()

deconnecterWiFi()
