'''Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.'''

import sys
from pymodbus.client import ModbusTcpClient
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

###   FUNCTIONS

def int16_to_int (register_value):
    if register_value >32767:
        register_value -= 65536
    return register_value
    
def uint32Stack(high_reg: int, low_reg: int) -> int:
    return (high_reg << 16) | low_reg

def acc32_to_int(high_register, low_register):
    # Ensure values are within 16-bit range
    high_register = high_register & 0xFFFF
    low_register = low_register & 0xFFFF
    # Combine registers
    combined_value = (high_register << 16) | low_register
    return combined_value

###   PARAMS
solarEdge_ip = '10.58.20.200'  # Replace with your inverter IP address
solarEdge_port = 1502  #TCP port of your inverter, for Solar Edge inverters 1502 typicaly is set as default 

modbusClient = ModbusTcpClient(solarEdge_ip, port=solarEdge_port)

disp=True
meter=True

disp = sys.argv[1].lower() == "true"
meter = sys.argv[2]

###   SCRAPING THE DATA FROM INVERTER
if modbusClient.connect():

    register1Start = 40072

    # Reading registers 71-107 (corresponding to 40072-40108) from the inverter of inverter's data
    response_1 = modbusClient.read_holding_registers(address=71, count=37, slave=1)

    if response_1.isError():
        print("Error reading registers 40072-40108")

    register2Start = 40207
    
    # Read registers 206-242 (corresponding to 40206-40242)
    if meter: 
        response_2 = modbusClient.read_holding_registers(address=206, count=37, slave=1)  # Fixed count
        if response_2.isError():
            print("Error reading registers 40206-40242")
        
    modbusClient.close()

    #Inverters Data
    AC_powerValueSF = int16_to_int(response_1.registers[40085 - register1Start])
    AC_powerValue = round(int16_to_int(response_1.registers[40084 - register1Start]) * (10**AC_powerValueSF),3)

    AC_lifetimeEnergyProductionSF = response_1.registers[40096-register1Start]
    AC_lifetimeEnergyProduction = round(acc32_to_int(response_1.registers[40094-register1Start],response_1.registers[40095 - register1Start])*(10**AC_lifetimeEnergyProductionSF),3)
    
    inverterStatus = response_1.registers[40108-register1Start] 
    
    phaseVoltageSF = int16_to_int(response_1.registers[40083-register1Start])
    A_phaseVoltage = round(response_1.registers[40080-register1Start] * (10**phaseVoltageSF),3)
    B_phaseVoltage = round(response_1.registers[40081-register1Start] * (10**phaseVoltageSF),3)
    C_phaseVoltage = round(response_1.registers[40082-register1Start] * (10**phaseVoltageSF),3)
    

    #Meter's Data
    if meter:
        powerFactorSF = int16_to_int(response_2.registers[40226 - register2Start]) 
        powerFactor = round(int16_to_int(response_2.registers[40222 - register2Start]) * (10**powerFactorSF),3)
    

        realPowerSF = int16_to_int(response_2.registers[40211 - register2Start])
        realPower = round(int16_to_int(response_2.registers[40207-register2Start]) * (10**realPowerSF),3)
    
        realEnergySF = int16_to_int(response_2.registers[40243-register2Start])
        totalExportedRealEnergy = round(uint32Stack(response_2.registers[40227-register2Start], response_2.registers[40228-register2Start]) * (10**realEnergySF),3)
        totalImportedRealEnergy = round(uint32Stack(response_2.registers[40235-register2Start], response_2.registers[40236-register2Start]) * (10**realEnergySF),3)

        #Calucalted Data
        siteConsumption = round(AC_powerValue - realPower,3)
        siteConsumption = round(siteConsumption,3) 
    #Displaing Data

    if (disp):
        print("Register values 40072-40108:", response_1.registers,"\n")
        if meter:
            print("Register values 40206-40242:", response_2.registers,"\n")

        if (AC_powerValue>=1000):
            print("Inverter producing:", AC_powerValue*0.001, "[kWh]\n")
        else:  
            print("Inverter producing:", AC_powerValue, "[W]\n")
        if meter:
            if (realPower>=1000 or realPower<=-1000):
                print("Grid Flow:",realPower*0.001,"[kWh]\n")
            else:
                print("Grid Flow:", realPower ,"[W]\n")
            if (siteConsumption>=1000 or siteConsumption<=1000):
                print("Site Consumption:", siteConsumption*0.001, "[kWh]\n" )
            else:
                print("Site Consumption:", siteConsumption, "[W]\n")

            print("Kilowats exported to the grid:", totalExportedRealEnergy, "[Wh]\n")
            print("Kilowats imported from the grid:", totalImportedRealEnergy, "[Wh]\n")
        
        print("Voltage on each phase: ",A_phaseVoltage, B_phaseVoltage, C_phaseVoltage,"\n")
        print("Kilowats lifetime produced: ",AC_lifetimeEnergyProduction,"\n")

    registry = CollectorRegistry()
    
    # Create gauges with the same names each iteration
    invStatus = Gauge('inverterStatus', 'Status of inverter',['device'], registry=registry)
    invLifetimeProduction = Gauge('lifetimeProduction', 'Lifetime energy production of inverter',['device'], registry=registry)
    invPowerProduction = Gauge('powerProduction', 'Power production of inverter',['device'], registry=registry)
    voltagePhaseA = Gauge('voltagePhase_A', 'Voltage on phase A',['device'], registry=registry)
    voltagePhaseB = Gauge('voltagePhase_B', 'Voltage on phase B',['device'], registry=registry)
    voltagePhaseC = Gauge('voltagePhase_C', 'Voltage on phase C',['device'], registry=registry)
    if meter:
        gridFlow = Gauge('gridFlow', 'Flow of power on connection point with the grid',['device'], registry=registry)
        pFactor = Gauge('powerFactor', 'Power factor',['device'], registry=registry)
        totExportedRealEnergy = Gauge('totalExportedRealEnergy', 'Total exported real energy from the site to the grid',['device'], registry=registry)
        totImportedRealEnergy = Gauge('totalImportedRealEnergy', 'Total imported real energy from the grid to the site',['device'], registry=registry)
    
    # Set values (replace with your actual measurements)
    invStatus.labels(device='inverterSolarEdge_SE30K').set(inverterStatus)
    invLifetimeProduction.labels(device='inverterSolarEdge_SE30K').set(AC_lifetimeEnergyProduction)
    invPowerProduction.labels(device='inverterSolarEdge_SE30K').set(AC_powerValue)
    voltagePhaseA.labels(device='inverterSolarEdge_SE30K').set(A_phaseVoltage)
    voltagePhaseB.labels(device='inverterSolarEdge_SE30K').set(B_phaseVoltage)
    voltagePhaseC.labels(device='inverterSolarEdge_SE30K').set(C_phaseVoltage)
    if meter:
        gridFlow.labels(device='Meter_no.1_site<->grid').set(realPower)
        pFactor.labels(device='Meter_no.1_site<->grid').set(powerFactor)
        totExportedRealEnergy.labels(device='Meter_no.1_site<->grid').set(totalExportedRealEnergy)
        totImportedRealEnergy.labels(device='Meter_no.1_site<->grid').set(totalImportedRealEnergy)
    

    # Push to gateway
    push_to_gateway('localhost:9091', job='energyData', registry=registry) 

else:
    print("Failed to connect to Modbus server")
