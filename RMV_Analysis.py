import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv

target_file_1='06-04-2017.csv'
target_file_2='07-04-2017.csv'
target_file_3='10-04-2017.csv'
df_1 = pd.read_csv(target_file_1)
df_2 = pd.read_csv(target_file_2)
df_3 = pd.read_csv(target_file_3)

#   Replace failed data collection with nan
df_1=df_1.replace(-30, np.nan)
df_2=df_2.replace(-30, np.nan)
df_3=df_3.replace(-30, np.nan)



global Header_Values
Header_Values=list(df_1.columns.values)


def graph_a_town(town_name,df,title):
    '''input a town name (first letter cap),dataframe and leading title. graph that town licensing and registration and datafram'''
    Date=df.iat[0,0]
    town_matches=[]
    for x in Header_Values:
        if town_name in x:
            town_matches+=[x]
    
    df.plot(x='Time', y=town_matches, title=title+' '+town_name+' '+Date)
    plt.ylabel('Current Wait Time (Minutes)')
    plt.ylim(-45,140)
    plt.gcf().autofmt_xdate()
    plt.show()
    #,xticks=[8,30]


def graph_a_town_two_days(town_name,df_1,df_2,title):
    '''input town name and two data frames, get them graphed together'''
    date_1=df_1.iat[0,0]
    date_2=df_2.iat[0,0]
    town_matches=[]
    for x in Header_Values:
        if town_name in x:
            town_matches+=[x]
    print town_matches
    temp_1=df_1[['Time']+town_matches].copy()
    temp_2=df_2[['Time']+town_matches].copy()
    temp_1=temp_1.rename(columns={town_matches[0]:date_1+' '+town_matches[0],town_matches[1]:date_1+' '+town_matches[1]})
    temp_2=temp_2.rename(columns={town_matches[0]:date_2+' '+town_matches[0],town_matches[1]:date_2+' '+town_matches[1]})

    ax = temp_1.plot()
    temp_2.plot(x='Time',ax=ax, title=title+' '+town_name+' two day comparison')
    plt.ylabel('Current Wait Time (Minutes)')
    plt.ylim(-45,140)
    plt.gcf().autofmt_xdate()
    plt.show()



def write_mean_wait_time(df):
    '''input a dataframe, output a csv same location.  date=csvname, same headers.  negatives omitted (failure / closed).'''
    df=df.replace(-15, np.nan)
    Date=df.iat[0,0]
    results_series=df.mean()
    results_series.to_csv(Date+' '+'mean_wait_times.csv')



#graph_a_town('Boston',df_1,'Figure 1:')
#graph_a_town('Watertown',df_1,'Figure 2:')
#graph_a_town('Fall River',df_1,'Figure 3:')

#graph_a_town('Boston',df_2,'Figure 4:')
#graph_a_town('Watertown',df_2,'Figure 5:')
#graph_a_town('Fall River',df_2,'Figure 6:')

#graph_a_town('New Bedford',df_2,'Figure 7:')
#graph_a_town('Attleboro',df_2,'Figure 8:')

#graph_a_town_two_days('Boston',df_2,df_3,'Figure 9:')
graph_a_town_two_days('Watertown',df_2,df_3,'Figure 10:')

