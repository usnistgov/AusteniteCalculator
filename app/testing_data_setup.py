import numpy as np
import pandas as pd

class dataSetup:
    def __init__(self) -> None:
        pass

    def read_data(master_data):
        lines = []
        with open(master_data) as f:
            lines = f.readlines()

        phases = int(lines[0])
        
        master_DF = pd.DataFrame({
        "Phase":[0]*phases,
        "Phase_Fraction":[0]*phases,
        "Phase_Fraction_StDev":[0]*phases,
        "Number_hkls":[0]*phases,
        "hkls":[np.nan]*phases,
        "Mean_nint":[0]*phases,
        "StDev_nint":[0]*phases
        })

        for i in (f + 1 for f in range(len(lines) - 1)):
            key_value_split = lines[i].split(': ')
            
            if(key_value_split[0] != 'hkls'):
                split_line = key_value_split[1].split(', ', phases)
        
            if(key_value_split[0] == 'hkls'):
                continue
            elif(i > 1):
                for j in range(len(split_line)):
                    split_line[j] = float(split_line[j])
                    master_DF.loc[j, key_value_split[0]] = split_line[j]
            else:
                for j in range(len(split_line)):
                    split_line[j] = split_line[j].strip()
                    master_DF.loc[j, key_value_split[0]] = split_line[j]
            
        return master_DF, phases



