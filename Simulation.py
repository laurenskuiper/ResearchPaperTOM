#!/usr/bin/env python

import csv
import matplotlib
import matplotlib.pyplot as plt
import random

def WindspeedLoader(filename):
    f = open(filename, 'r')
    dates = []
    speeds = []
    for line in f.readlines():
        line = line.rstrip('\n')
        values = []
        if line:
            x = line.split(",")
            if len(x) > 1:
                # Filtered out all empty lines
                if x[1][3] == '9':
                    # Only year 2019 taken into account 
                    values.append(int(x[1])) # Date
                    values.append(int(x[2])) # Hour
                    speeds.append(int(x[4]) / 10) # FH --> Average wind speed in m/s that hour
                    dates.append(values)
    return dates, speeds

def CalculateDemand(filename):
    with open(filename) as data:
        reader = csv.reader(data, delimiter=",")
        fractions = []
        count = 0
        average = 0 
        for row in reader:
            if len(row) > 1:
                count += 1
                start_time = row[0]
                end_time = row[1]
                fraction = row[3]
                average = average + float(fraction)
                if ((count & 3) == 0): # Check if count is multiple of 4
                    fractions.append(average * 2832 * 2985) # Avg of current hour * average yearly demand * number of households
                    average = 0
                    count = 0
                else:
                    pass
    return fractions

def TurbineOutput(speeds):
    output = []
    for i in speeds:
        value = (((0.5 * 1.23 * 10660 * (i**3)* 0.45) / 1000) * 4) # Power generation formula multiplied by amount of turbines / 1000 for KW 
        output.append(value)
    
    return output

def PlotSpeeds(speeds):
    fig, ax = plt.subplots(figsize=(30,15))

    ax.plot(speeds)
    ax.set(xlabel='HOURS 2019', ylabel='WIND SPEEDS IN M / S',
            title='WIND SPEEDS EELDE 2019')
    ax.grid()

    #plt.show()

    fig.savefig("windspeeds.png")

def PlotDemand(demand):
    fig, ax = plt.subplots(figsize=(30,15))

    ax.plot(demand)
    ax.set(xlabel='HOURS 2019', ylabel='ELECTRICITY DEMAND IN KWH',
            title='ELECTRICITY DEMAND PER HOUSEHOLD 2019')
    ax.grid()

    #plt.show()

    fig.savefig("demand.png")

def PlotCurtailment(curtailment, hours):
    fig, ax = plt.subplots(figsize=(30,15))

    ax.plot(hours, curtailment)
    ax.set(xlabel='HOURS 2019', ylabel='CURTAILMENT IN KW',
            title='CURTAILMENT PER HOUR OVER 2019')
    ax.grid()

    plt.show()

    fig.savefig("curtailment2019.png")

def PlotShortages(shortages, hours):
    fig, ax = plt.subplots(figsize=(30,15))

    ax.plot(hours, shortages)
    ax.set(xlabel='HOURS 2019', ylabel='SHORTAGES IN KW',
            title='SHORTAGES PER HOUR OVER 2019')
    ax.grid()

    plt.show()

    fig.savefig("shortages2019.png")


def Forecaster(speeds, demand, EX_S, Max_Storage):
    EX_M = 0 # Expected Matches
    F_hour = 0

    # Forecasted Situation
    for s, d in zip(speeds[0:48], demand[0:48]):
        F_hour += 1
        Pred = random.uniform((s*0.975), (s*1.025)) # Randomizer according to accuracy
        F_output = (((0.5 * 1.23 * 10660 * (Pred**3)* 0.45) / 1000) * 4) # Power generation formula multiplied by amount of turbines / 1000 for KW 
        
        if F_output < d:
            EX_deficit = d - F_output
            EX_S -= (EX_deficit * 2)
            if EX_S < 0:
                EX_S = 0
                return 'Shortage<2'
        elif F_output == d:
            EX_M += 1
        else:
            EX_surplus = F_output - d
            if (EX_surplus / 60) < 1500: # Alkaline Capacity
                EX_S += (EX_surplus * 0.7) * 0.83 # Taking Alkaline Electrolyser and Curtailment % based on literature into account
                if EX_S > Max_Storage:
                    EX_S = Max_Storage
                    return 'Curtailment<2'
    
    for s, d in zip(speeds[48:168], demand[48:168]):
        F_hour += 1
        Pred = random.uniform((s*0.935), (s*1.065)) # Randomizer according to accuracy
        F_output = (((0.5 * 1.23 * 10660 * (Pred**3)* 0.45) / 1000) * 4) # Power generation formula multiplied by amount of turbines / 1000 for KW 
        
        if F_output < d:
            EX_deficit = d - F_output
            EX_S -= (EX_deficit * 2)
            if EX_S < 0:
                EX_S = 0
                return 'Shortage<7'
        elif F_output == d:
            EX_M += 1
        else:
            EX_surplus = F_output - d
            if (EX_surplus / 60) < 1500: # Alkaline Capacity
                EX_S += (EX_surplus * 0.7) * 0.83 # Taking Alkaline Electrolyser and Curtailment % based on literature into account
                if EX_S > Max_Storage:
                    EX_S = Max_Storage
                    return 'Curtailment<7'
    
    for s, d in zip(speeds[168:336], demand[168:336]):
        F_hour += 1
        Pred = random.uniform((s*0.90), (s*1.10)) # Randomizer according to accuracy
        F_output = (((0.5 * 1.23 * 10660 * (Pred**3)* 0.45) / 1000) * 4) # Power generation formula multiplied by amount of turbines / 1000 for KW 
        
        if F_output < d:
            EX_deficit = d - F_output
            EX_S -= (EX_deficit * 2)
            if EX_S < 0:
                EX_S = 0
                return 'Shortage<14'
        elif F_output == d:
            EX_M += 1
        else:
            EX_surplus = F_output - d
            if (EX_surplus / 60) < 1500: # Alkaline Capacity
                EX_S += (EX_surplus * 0.7) * 0.83 # Taking Alkaline Electrolyser and Curtailment % based on literature into account
                if EX_S > Max_Storage:
                    EX_S = Max_Storage
                    return 'Curtailment<14'

def main():
    Dates, Speeds = WindspeedLoader('Windspeeds.txt')
    Demand = CalculateDemand('DemandProfiles.csv')
    Output = TurbineOutput(Speeds)

    Storage = 845352 # 100 % of capacity is stored initially
    Max_Storage = 845352 # 10 % of annual demand is the max storage capacity 
    Num_S = 0
    Match = 0
    Num_C = 0
    Hours = 0
    EX_S = 0 # Expected Shortage Hours
    EX_C = 0 # Expected Curtailment Hours
    ShortageAmounts = []
    ShortageHours = []
    CurtailmentAmounts = []
    CurtailmentHours = []
    for o, d in zip(Output, Demand):
        Hours += 1
        Inp_speeds = Speeds[int(Hours):int(Hours + 336)]
        Inp_demand = Demand[int(Hours):int(Hours + 336)]

        Prediction = Forecaster(Inp_speeds, Inp_demand, Storage, Max_Storage)

        if (Prediction == 'Shortage<2') or (Prediction == 'Shortage<7') or (Prediction == 'Shortage<14'):
            EX_S += 1
            Turbines = 1
            Multiplier = 1 # Store all electricity if shortage is expected
            Multiplier2 = 0
        elif Prediction == 'Curtailment<14':
            EX_C += 1
            Turbines = 1 # 4 active Turbines if Curtailment is expected in 14 days
            Multiplier = 0.83
            Multiplier2 = 0.17
        elif Prediction == 'Curtailment<7':
            EX_C += 1
            Turbines = 0.25 # 1 active Turbine if Curtailment is expected in 7 days
            Multiplier = 0.83
            Multiplier2 = 0.17
        elif Prediction == 'Curtailment<2':
            EX_C += 1
            Turbines = 0.0 # 0 active Turbines if Curtailment is expected in 2 days
            Multiplier = 0.83
            Multiplier2 = 0.17
        else:
            Turbines = 1.0
            Multiplier = 0.83
            Multiplier2 = 0.17

        o = o * Turbines # Output based on amount of turbines

        if o < d:
            deficit = d - o
            Storage -= (deficit * 2) # Take Fuel Cell into account
            if Storage < 0:
                Num_S += Storage * -1
                ShortageAmounts.append(Storage * -1) # Append Shortage amount to a list and untake Fuel Cell into account
                ShortageHours.append(Hours)
                Storage = 0
        elif o == d:
            Match += 1
        else:
            surplus = o - d
            if (surplus / 60) < 1500: # Alkaline Capacity
                Storage += (surplus * 0.7) * Multiplier # Taking Alkaline Electrolyser and Curtailment % based on literature into account
                if Storage > Max_Storage:
                    Num_C += Storage - Max_Storage
                    CurtailmentAmounts.append(Storage - Max_Storage + (surplus * Multiplier2))
                    CurtailmentHours.append(Hours)
                    Storage = Max_Storage
            else:
                Num_C += surplus
                CurtailmentAmounts.append(surplus)
                CurtailmentHours.append(Hours)
        
        Multiplier = 0.83
        Multiplier2 = 0.17
        Turbines = 1.0
            
        print(o, d, Storage, Hours, Prediction)

    print(len(CurtailmentHours), len(ShortageHours), Num_C, Num_S, EX_S, EX_C)

    #PlotCurtailment(CurtailmentAmounts, CurtailmentHours)
    #PlotShortages(ShortageAmounts, ShortageHours)
    #PlotDemand(Demand)
    #PlotSpeeds(Speeds)


if __name__ == "__main__":
    main()