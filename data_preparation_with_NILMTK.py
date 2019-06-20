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
metergroup = dataset.buildings[4].elec 

#Declare a Pandas DataFrame
df = pd.DataFrame(columns=['Start Time','End Time','Active Appliances'])

# type='laptop computer','computer monitor','active speaker','washing machine','computer'dish washer'
for meter in metergroup.submeters().meters:
    print('---------------- instance :',meter.identifier.instance ,' - ', meter.label(),' ----------------')
    print ("min_off_duration :", meter.min_off_duration(),
           "\t min_on_duration :", meter.min_on_duration() ,
           "\t on_power_threshold :", meter.on_power_threshold())
    # Get the activation series (List of Pandas Series )
    activation = meter.activation_series()
    
    # foreach activation in the Series
    for act in activation:
        #print(act)
        #foreach value in the Series.index ( data type :)
        for i in act.index:
            # calcul of start 
            if(i.minute<=30):
                start_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=0)
                #end time
                end_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=30)
                #print(i ,' ===>',start_time , ' @@', end_time)
            else:
                start_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=i.hour, minute=30)
                #end time
                if(i.hour==23):
                    hour=0
                else:
                    hour=i.hour+1
                end_time = pd.Timestamp(year=i.year, month=i.month, day=i.day, hour=hour, minute=0)
                #print(i ,' ===>',start_time , ' @@', end_time)
                
            # Add row to data
            if(df.index.contains(start_time)):
                #update the row 'Active Appliances'
                #appliances_set = df.loc[start_time]['Active Appliances']
                df.loc[start_time]['Active Appliances'].add(meter.identifier.instance)
                #print(type(df.loc[start_time]['Active Appliances']))
            else:
                df.loc[start_time]=[start_time,end_time,set([meter.identifier.instance])]
                         
        # end activation
        #print(len(start_times))
       
        
    print('\n')
    #end for meter
#print(df)    
# Export to CSV Format 
file_name = EXPORT_PATH+'house_'+str(metergroup.building())+'.csv'
df.to_csv(file_name,index=False, sep='\t', encoding='utf-8')
