import traci
import time
import traci.constants as tc
import pytz
import datetime
from random import randrange
import pandas as pd


def getdatetime():
    utc_now = pytz.utc.localize(datetime.datetime.utcnow())
    currentDT = utc_now.astimezone(pytz.timezone("Asia/Ho_Chi_Minh"))
    DATIME = currentDT.strftime("%Y-%m-%d %H:%M:%S")
    return DATIME


sumoCmd = ["sumo", "-c", "osm.sumocfg"]
traci.start(sumoCmd)


packVehicleData = []
packTLSData = []
packBigData1 = []
packBigData2 = []
packBigData3 = []


while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    vehicles = traci.vehicle.getIDList()
    trafficlights = traci.trafficlight.getIDList()

    timeSimulation = traci.simulation.getTime()
    TIME = 5
    MAXSPEED = 16  # value in m/s (16 m/s = 57.6 km/hr)
    traci.vehicletype.setMaxSpeed('veh_passenger', MAXSPEED)

    for i in range(0, len(vehicles)):

        vehid = vehicles[i]
        nextTLS = traci.vehicle.getNextTLS(vehicles[i])
        spd = round(traci.vehicle.getSpeed(vehicles[i]), 2)
        acc = round(traci.vehicle.getAcceleration(vehicles[i]), 2)
        idd = traci.vehicle.getLaneID(vehicles[i])

#                 ##----------CONTROL Vehicles and Traffic Lights----------##

        currentSpeed = traci.vehicle.getSpeed(vehicles[i])
        maxAcceleration = round((MAXSPEED - currentSpeed)/TIME, 2)
        currentAcceleration = traci.vehicle.getAcceleration(vehicles[i])
        nextTLS = traci.vehicle.getNextTLS(vehicles[i])

        for j in range(0, len(nextTLS)):
            trafficLight = nextTLS[j]
            trafficLightId = trafficLight[0]
            trafficLightState = trafficLight[3]
            trafficLightDistance = trafficLight[2]
            trafficLightDuration = traci.trafficlight.getPhaseDuration(
                trafficLightId)
            trafficLightTimeNextState = traci.trafficlight.getNextSwitch(
                trafficLightId)
            trafficLightCurrentTime = trafficLightTimeNextState - timeSimulation

            if trafficLightDistance <= maxAcceleration * 1/2 * pow(TIME, 2) and trafficLightCurrentTime > TIME and trafficLightCurrentTime <= 10 and trafficLightState == "G":

                traci.vehicle.setAcceleration(
                    vehicles[i], maxAcceleration, TIME)

        fuelConsumption = round(
            traci.vehicle.getFuelConsumption(vehicles[i]), 2)
        co2 = round(traci.vehicle.getCO2Emission(vehicles[i]), 2)
        co = round(traci.vehicle.getCOEmission(vehicles[i]), 2)

        packBigData3.append(
            [timeSimulation, vehicles[i], fuelConsumption, co2, co])
        packBigData1.append([timeSimulation, vehid, spd, maxAcceleration, acc])

traci.close()

# Generate Excel file
columnnames1 = ['time', 'vehid',   'spd', "max acceleration",
                "acceleration"]
columnnames2 = ['time', 'vehid',   'spd', "max deceleration",
                "acceleration", "trafficLight", "state", "distance", "duration", "current time"]
columnnames3 = ["time", "vehicle id", "fuel", "co2", "co"]
#        'tflight', 'tl_state', 'tl_phase_duration', 'tl_lanes_controlled', 'tl_program', 'tl_next_switch']
dataset1 = pd.DataFrame(packBigData1, index=None, columns=columnnames1)
# dataset2 = pd.DataFrame(packBigData2, index=None, columns=columnnames2)
dataset3 = pd.DataFrame(packBigData3, index=None, columns=columnnames3)
dataset3.to_excel("emission.xlsx", index=False)
# dataset2.to_excel("action2.xlsx", index=False)
dataset1.to_excel("dataAfter1.xlsx", index=False)
time.sleep(5)
