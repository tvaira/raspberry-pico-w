import sys
import platform
import os
import machine
import network

#print(sys.implementation)
#print(sys.modules)
#print(sys.version)
#print(platform.platform())
#print(os.uname())

print("Carte : " + str(sys.implementation._machine))
print("Implementation : " + str(sys.implementation.name))
majeur, mineur, patch = sys.implementation.version
print("Version : " + str(majeur) + "." + str(mineur) + "." + str(patch))
print("Plateforme : " + str(sys.platform))
print(str(sys.byteorder) + " endian")

print("Frequence : " + str(machine.freq()) + " Hz")

if hasattr(network, "WLAN"):
   print("WLAN : ok")
