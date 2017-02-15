from networktables import NetworkTables
import sys
import time

NetworkTables.initialize(server='10.2.79.101')
print('Waiting to connect...')
while NetworkTables.isConnected() == False:
    time.sleep(0.1)

nt = NetworkTables.getTable("Gear")

res1= nt.putValue("angle", -999)
res2 = nt.putValue("distance", -999)
res3 = nt.putValue("eyes", False)

if res1 == False or res2 == False or res3 == False:
    print("failed to put value")
