import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import json
import time
import pickle
import ugregmod
from sys import exit
start_time = time.time()
#
#
runde = 3
if runde == 99 or runde == 0:
    ugregmod.ugregmod('TEST', runde)
else:
    ugregmod.ugregmod('XXC-902', runde)

duration = time.time() - start_time
if runde == 99:
    yrs = 10
elif runde == 0:
    yrs = 25
elif runde == 1:
    yrs = 15
elif runde == 2:
    yrs = 20
elif runde == 3:
    yrs = 40
pery = round(duration / yrs, 2)
print("--- %s seconds ---" % (time.time() - start_time))
print('   per year: '+str(pery)+' seconds')
perDT = round(duration / (yrs * 32), 3)
print('   per DT: '+str(perDT)+' seconds')
