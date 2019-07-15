from __future__ import print_function, division
import time
from matplotlib import rcParams
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from six import iteritems
import warnings
warnings.filterwarnings('ignore')
%matplotlib inline
rcParams['figure.figsize'] = (13, 6)
from nilmtk import *
from nilmtk.utils import print_dict


# step 0: declare the path 
DATASET_PATH = '/home/acer/ukdale2015/ukdale.h5'
EXPORT_PATH ='/home/acer/Admin NILMTK/dataset/'

# step 1 : load dataset
dataset = DataSet(DATASET_PATH)


# step 2 : select the MeterGroup foreach building
metergroup = dataset.buildings[5].elec 

#Declare a Pandas DataFrame
df = pd.DataFrame(columns=['Start Time','End Time','Active Appliances'])

# type='laptop computer','computer monitor','active speaker','washing machine','computer'dish washer'
for meter in metergroup.submeters().meters:
    print('---------------- instance :',meter.identifier.instance ,' - ', meter.label(),' ----------------')
    print ("min_off_duration :", meter.min_off_duration(),
           "\t min_on_duration :", meter.min_on_duration() ,
           "\t on_power_threshold :", meter.on_power_threshold())
    # Get the activations series (List of Pandas Series )
    activations = meter.activation_series()
    
    # foreach activation in the Series
    for act in activations:
        #print(act)
        active_power= np.float32(0.0)
        active_power_reset_value = False
        #foreach value in the Series.index ( data type :)
        for i in act.index:  
            #test if power reset value is True 
            if(active_power_reset_value):
                # Add row to data to DataFrame
                meter_string = str(meter.identifier.instance) +"-"+str(active_power)
                #print(meter_string)
                if(df.index.contains(start_time)):
                    #update the row 'Active Appliances' in the DataFrame
                    df.loc[start_time]['Active Appliances'].add(meter_string) 
                else:
                    #added the row to DataFrame
                    df.loc[start_time]=[start_time,end_time,set([meter_string])]
                #Reset active_power value and reset active_power_reset_value
                active_power= np.float32(0.0)
                active_power_reset_value = False
            else:
                # Agregate the active power value
                active_power+= act.get(i)
            
            # calcul of : start_time & end_time & active_power
            if(i.minute<=30):
                #start time
                start_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=0)
                #end time
                end_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=30)
                #active power reset test
                if(i.minute==30):
                    if(i.second>=54):
                        active_power_reset_value = not (i.minute==30 & i.second>=54) 
                    
                #print('index is ',i ,' ===>',start_time , ' @@', end_time , ' @@', active_power, ' @@',act.get(i)) 
            else:
                #start time
                start_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=30)
                #end time
                if(i.hour==23):
                    hour=0
                else:
                    hour=i.hour+1
                end_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=hour, minute=0)  
                #active power reset test 
                if(i.minute==59):
                    if(i.second>=54):
                        active_power_reset_value = not (i.minute==59 & i.second>=54)
                
                #print('index is ',i ,' ===>',start_time , ' @@', end_time , ' @@', active_power, ' @@',act.get(i)) 
                
            
                         
        # end activation
        #print(len(start_times))
       
        
    print('\n')
    #end for meter
#print(df)    
# Export to CSV Format 
file_name = EXPORT_PATH+'house_'+str(metergroup.building())+'.csv'
df.to_csv(file_name,index=False, sep='\t', encoding='utf-8')
