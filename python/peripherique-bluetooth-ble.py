# La transmission UART sur BLE ne fait pas partie des profils définis par Bluetooth SIG. C’est un service personnalisé par Nordic Semiconductor. Nordic Semiconductor (fabricant des puces nRFxxx) a créé le Nordic UART Service (NUS) qui est un exemple d’émulation d’un port série sur BLE. Cela inclut le service "Nordic UART" dont l’UUID spécifique est 6E400001-B5A3-F393-E0A9-E50E24DCCA9E.
#
# Ce service présente deux caractéristiques (l’une pour l’émission et l’autre pour la réception) :
# - Caractéristique RX (UUID: 6E400002-B5A3-F393-E0A9-E50E24DCCA9E) : le client peut envoyer des données au périphérique en écrivant dans la caractéristique de réception du service.
# - Caractéristique TX (UUID: 6E400003-B5A3-F393-E0A9-E50E24DCCA9E) : si client a activé les notifications pour cette caractéristique, le serveur peut lui envoyer des données en tant que notifications.
#
# BLE NUS est donc un service BLE propriétaire, en quelque sorte l’équivalent du profil SPP (Serial Port Profile), basé sur le protocole RFCOMM, du Bluetooth Classic.

import machine
import bluetooth
import struct
import time
import machine
import ubinascii
from ble_advertising import advertising_payload
from micropython import const

# Le nom du périphérique
nomPeripherique = "picow"

# L'objet Bluetooth BLE
ble = bluetooth.BLE()

# Les codes _event_
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_INDICATE_DONE = const(20)
_IRQ_GATTC_READ_RESULT = const(15)
_IRQ_GATTC_READ_DONE = const(16)
_IRQ_GATTC_WRITE_DONE = const(17)
_IRQ_GATTC_NOTIFY = const(18)

# Les indicateurs disponibles pour les caractéristiques et les descripteurs
_FLAG_BROADCAST = const(0x0001)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# Le service "Nordic UART"
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

# Pour gérer les connexions
connexions = set()

# Pour la transmission des données
payload = advertising_payload(name=nomPeripherique, services=[_UART_UUID])

# Les fonctions
def estConnecte():
    return len(connexions) > 0

def envoyer(handleTX, donnees):
    for connexion in connexions:
        ble.gatts_notify(connexion, handleTX, donnees)

def annoncerPeripherique(intervalle=500000):
    print("Nom peripherique : " + nomPeripherique)
    print("Demarre l'annonce (advertising)")
    ble.gap_advertise(intervalle, adv_data=payload)

def traiterEvenement(evenement, data):
    if evenement == _IRQ_CENTRAL_CONNECT:
        # Une connexion sur le périphérique
        connexion, typeAdresse, adresse = data
        print("Connecte : ", ubinascii.hexlify(adresse))
        connexions.add(connexion)
    elif evenement == _IRQ_CENTRAL_DISCONNECT:
        # Une déconnexion sur le périphérique
        connexion, typeAdresse, adresse = data
        print("Deconnecte : ", ubinascii.hexlify(adresse))
        if(ubinascii.hexlify(adresse) != b'000000000000'):
            connexions.remove(connexion)
        # Démarre une annonce
        annoncerPeripherique()
    elif evenement == _IRQ_GATTS_WRITE:
        # Un client a envoyé des données sur une charactéristique ou un descripteur
        connexion, valeur = data
        donnees = ble.gatts_read(valeur)
        print("Donnees recues : ", donnees)
        # echo
        envoyer(handleTX, donnees)
    elif evenement == _IRQ_GATTS_INDICATE_DONE:
        # Un client a acquitté une indication
        # status = 0 -> succès
        connexion, valeur, status = data
        print("_IRQ_GATTS_INDICATE_DONE")
    elif evenement == _IRQ_GATTC_READ_RESULT:
        # A gattc_read() has completed
        connexion, valeur, status = data
        print("_IRQ_GATTC_READ_RESULT")
    elif evenement == _IRQ_GATTC_READ_DONE:
        # A gattc_read() has completed
        # status = 0 -> succès
        connexion, valeur, status = data
        print("_IRQ_GATTC_READ_DONE")
    elif evenement == _IRQ_GATTC_WRITE_DONE:
        # A gattc_write() has completed
        # status = 0 -> succès
        connexion, valeur, status = data
        print("_IRQ_GATTC_WRITE_DONE")
    elif evenement == _IRQ_GATTC_NOTIFY:
        # A server has sent a notify request
        connexion, valeur, status = data
        print("_IRQ_GATTC_NOTIFY")

def initialiserBluetooth():
    ble.active(True)
    ble.irq(traiterEvenement)
    ((handleTX, handleRX),) = ble.gatts_register_services ((_UART_SERVICE,))
    annoncerPeripherique()
    return (handleTX, handleRX)

# Led embarquée
led = machine.Pin("LED", machine.Pin.OUT)

# Capteur de température embarquée
def getTemperature():
   tensionPICO = 3.3
   quantumCAN = tensionPICO / 65535
   capteurTemperature = machine.ADC(machine.ADC.CORE_TEMP)
   valeurCAN = capteurTemperature.read_u16()
   tensionCAN = valeurCAN * quantumCAN
   temperature = 27 - (tensionCAN - 0.706)/0.001721
   return temperature

def envoyerTemperature(notify=False, indicate=False):
    temperature = getTemperature()
    print("Temperature : %.2f C" % temperature)
    print("Donnees envoyees : ", ubinascii.hexlify(int(temperature * 100).to_bytes(2, "little")))
    # https://docs.python.org/3/library/struct.html
    # < little-endian
    # h short
    ble.gatts_write(handleTX, struct.pack("<h", int(temperature * 100)))
    if notify or indicate:
        for connexion in connexions:
            if notify:
                ble.gatts_notify(connexion, handleTX)
            if indicate:
                ble.gatts_indicate(connexion, handleTX)

# Le programme
(handleTX, handleRX) = initialiserBluetooth()

n = 0
while True:
    if n % 10 == 0:
        envoyerTemperature(notify=True, indicate=False)
    led.toggle()
    time.sleep_ms(1000)
    n += 1
