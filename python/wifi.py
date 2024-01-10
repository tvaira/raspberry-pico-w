import time
import network
import ubinascii

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
      adresseMAC = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
      print('Adresse MAC = ' + adresseMAC)
      print('Canal = ' + str(wlan.config('channel')))
      print('TX Power = ' + str(wlan.config('txpower')))

def deconnecterWiFi():
   # Déconnexion
   wlan.disconnect()

connecterWiFi()

# ...

deconnecterWiFi()
