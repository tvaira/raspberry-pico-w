import machine

tensionPICO = 3.3
print("Tension Pico : " + str(tensionPICO) + " V")
quantumCAN = tensionPICO / 65535
print("Quantum CAN : " + str(quantumCAN*1000) + " mV")
capteurTemperature = machine.ADC(machine.ADC.CORE_TEMP)
print("Entree CAN : " + str(machine.ADC.CORE_TEMP))
valeurCAN = capteurTemperature.read_u16()
print("Valeur CAN : " + str(valeurCAN))
tensionCAN = valeurCAN * quantumCAN
print("Tension CAN : " + str(tensionCAN) + " V")
temperature = 27 - (tensionCAN - 0.706)/0.001721
print("Conversion : " + str(temperature) + " C")
print("Temperature : " + str(round(temperature)) + " C")
