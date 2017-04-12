#!/usr/bin/python

import os.path,urllib2,requests,datetime,csv,time,logging
from bs4 import BeautifulSoup

##      Current to-do list
##      Get crons working replace while loop w/ system execution
##      potentially change folder location from defined within program (hard-coded=bad) to variable (?)
##      find a way to test URL request time outs without having to encounter them in the wild





global folder_location
#folder_location = '/Users/davidterwilliger/Desktop/Dt/Scrape/'
folder_location=''
def get_current_wait_times(town_name):
    '''takes town_name which is a string {first letter cap} completes its URL, scrapes the two times [licensing and registration] returns them as two legnth list containing strings'''
        
        #   Makes the complete URL, Martha's Vinyard is handled differently by the template
    if town_name=='Martha%27s%20Vineyard':
        url = 'http://www.massrmv.com/index/tabid/3353/ctl/accessible/mid/9589/Default.aspx?Name=Martha%27s%20Vineyard'
    else:
        url = 'http://www.massrmv.com/index/tabid/3353/ctl/accessible/mid/9589/Name/'+str(town_name)+'/Default.aspx'

        #   Creates soup of URL to search for specifi class
    try:
        r  = requests.get(url)
    except Exception, e:
        #errors fill the array with -30s for debugging
        f = open('log.txt', 'w')
        f.write('Failure with requests.get(URL)'+url+' - %s' % e)
        f.close()
        print 'Houston we have a problem.  Most likely a timed out request', url
        return [-30,-30]
    data = r.text
    soup = BeautifulSoup(data, "html.parser")
    
        #   Results are stored as two specific classes within the HTML.  Each are retrieved and stored as a string
    results=[]    
        #   Licensing stored first
    spans = soup.find_all('span', attrs={'id':'dnn_ctr9589_ViewBranchAccessible_lblLicensing'})
    for span in spans:
        #   Try is used incase type conversion fails -30 is stored as a value to indicate a failure
        try:
            results+=[str(span.string)]
        except Exception, e:
            print 'error with town licensing: ',town_name,' Troublesome string is: ', span.string
            f = open('log.txt', 'w')
            f.write('Trouble handling string from ID'+url+' - %s' % e)
            f.close()
            results+=[-30]
            #   Should eventually print to a fail_log
        #   Registration stored second    
    spans = soup.find_all('span', attrs={'id':'dnn_ctr9589_ViewBranchAccessible_lblRegistration'})
    for span in spans:
        #   Try is used incase type conversion fails -30 is stored as a value to indicate a failure
        try:
            results+=[str(span.string)]
        except Exception, e:
            print 'error with town registration: ',town_name,' Troublesome string is: ', span.string
            f = open('log.txt', 'w')
            f.write('Trouble handling string from ID'+url+' - %s' % e)
            f.close()            
            results+=[-30]
    return results


def make_new_csv(current_date,list_of_towns):
    '''input date and list of towns.  Make a new csv date.csv at !!global!! filelocation.  Headers are 'date, time then two each of each town name'''
    name=str(current_date)
    print name,'this is the current date for the file_name recently created'
    list_of_towns=['Attleboro','Boston','Braintree','Brockton','Chicopee','Easthampton','Fall River','Greenfield','Haverhill','Lawrence','Leominster','Lowell','Marthas Vineyard','Milford','Nantucket','Natick','New Bedford','North Adams','Pittsfield','Plymouth','Revere','Roslindale','South Yarmouth','Springfield','Taunton','Watertown','Wilmington','Worcester']
    f = open(folder_location+name+'.csv', 'wb')
    header=['Date','Time']
    for towns in list_of_towns:
        header+=[towns+' Licensing',towns +' Registration']
    wr = csv.writer(f)
    wr.writerow(header)    


def check_for_today_csv(current_date):
    '''returns if there is a file created or not.  One line function done simply to rename function to make the call more obvious'''
    file_name=folder_location+current_date+'.csv'
    return os.path.exists(file_name)

def add_a_reading(date,current_time,list_of_towns):
    '''input date,time,list_of_towns. opens and writes results to current file makes file if it doesnt exist '''
    #   Check and see if file exists, make a new file if it doesn't.  format is global file location+date+.csv
    if check_for_today_csv(current_date)==False:
        make_new_csv(current_date,list_of_towns)
    
    #   Results are date time 2x each town
    results=[]
    results+=[current_date,current_time]
    
    #   Results array filled with strings
    for town in list_of_towns:
        results+=get_current_wait_times(town)

    #   Convert results from strings to numbers exclude first two
    results=convert_results_to_minutes(results)

    #   Add results to CSV
    file_name=folder_location+current_date+'.csv'
    if len(results)==58:
        with open(file_name,'ab') as resultFile:
            wr = csv.writer(resultFile, dialect='excel')
            wr.writerow(results)
    else:
        print results,'houston we have a problem dropped result'
        #should log this somehow.  a town or entry got dropped.  Hasn't triggered in a while

def convert_results_to_minutes(results):
    '''input: list [first two entries are date,time then strings of wait times.  convert strings to numbers rounded to minute return same array'''

    #   Array has date and time, ignore first two.  
    for a in range(2,len(results)):
        #   Temporary holder for variable to check
        string_holder=results[a]
        #   Easiest possible outcome.  
        if string_holder=='No wait time':
            results[a]=0

        #   Closed should be graphed as -15 so that its obvious
        elif string_holder=='Closed':
            results[a]=-15

        #   If hours is in string its of format '1 hour, 13 minutes, 50 seconds'
        #   Return 60*hour plus minutes ignore seconds
        elif 'hour' in string_holder:
            try:
                number_of_hours=int(string_holder[:string_holder.index('hour')])
                string_holder=string_holder[(string_holder.index(',')+1):]
                number_of_minutes=int(string_holder[:string_holder.index('minute')])
                results[a]=number_of_hours*60+number_of_minutes
            except Exception, e:
                print 'string conversion error caused by', string_holder
                f = open('log.txt', 'w')
                f.write('string conversaion error caused by [hour in string]'+string_holder+' - %s' % e)
                f.close()            
                results[a]=-30

        #   If no hours in string return just the minutes ignore seconds.  Format: '14 minutes, 28 seconds'
        elif 'minute' in string_holder:
            try:
                results[a]=int(string_holder[:string_holder.index('minute')])
            except Exception, e:
                print 'string conversion error caused by', string_holder
                f = open('log.txt', 'w')
                f.write('string conversaion error caused by[minute in string but not hour] '+string_holder+' - %s' % e)
                f.close()            

        #   Just single digit seconds should count as zero rare, but crashed program a few times until logging detected.
        elif 'second' in string_holder:
            results[a]=0

        else:
            results[a]=-30
            print 'Houston we have a problem.  The string was not handled ', string_holder
            #this needs to be logged somehow
    return results


list_of_towns=['Attleboro','Boston','Braintree','Brockton','Chicopee','Easthampton','Fall%20River','Greenfield','Haverhill','Lawrence','Leominster','Lowell','Martha%27s%20Vineyard','Milford','Nantucket','Natick','New%20Bedford','North%20Adams','Pittsfield','Plymouth','Revere','Roslindale','South%20Yarmouth','Springfield','Taunton','Watertown','Wilmington','Worcester']
current_date=time.strftime("%d-%m-%Y")
current_time=str(time.strftime("%H:%M:%S"))

count=0
delay_seconds=900

    #comment this out to only run once (when cron implemented)
    #A naughty while true loop
while True:
    count+=1
    current_time=str(time.strftime("%H:%M:%S"))
    current_date=time.strftime("%d-%m-%Y")
    add_a_reading(current_date,current_time,list_of_towns)
    print 'hi, count is:',count, 'current time is: ', current_time,'current date is: ', current_date
    time.sleep(delay_seconds)
    

    


# python /Users/davidterwilliger/Desktop/Dt/Scrap/test_3.py
# python /Users/foo/Desktop/Dt/Scrap/test_3.py





#   Cron Job
#   python /Users/davidterwilliger/Desktop/Dt/Scrap/test_3.py
#This will run from 7.00 until 19.45, every 15 minutes:

#*/15    07-19        *     * *     /path/script
#If you want it to run until 19.00 then you have to write two lines:

#*/15    07-18        *     * *     /path/script
#0          19        *     * *     /path/script

#*/15    08-19        *     * *     python /Users/davidterwilliger/Desktop/Dt/Scrap/test_3.py


# Error logging

# Traceback (most recent call last):
#   File "<pyshell#1>", line 1, in <module>
#     add_a_reading(date,time,list_of_towns)
#   File "C:\Users\Devlab\Desktop\Dt\Scrap\test_1.py", line 75, in add_a_reading
#     results=convert_results_to_minutes(results)
#   File "C:\Users\Devlab\Desktop\Dt\Scrap\test_1.py", line 99, in convert_results_to_minutes
#     results[a]=int(string_holder[:string_holder.index('minute')])
# ValueError: invalid literal for int() with base 10: '1 hour, 7 '

##logging.basicConfig(filename='myapp.log', level=logging.DEBUG, 
##                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
##logger=logging.getLogger(__name__)

#try:
#    x=1/0
#except Exception, e:
#    f = open('log.txt', 'w')
#    f.write('An exceptional thing happed - %s' % e)
#    f.close()
    
##Traceback (most recent call last):
##  File "<pyshell#1>", line 1, in <module>
##    add_a_reading(date,time,list_of_towns)
##  File "C:\Users\Devlab\Desktop\Dt\Scrap\test_1.py", line 75, in add_a_reading
##    results=convert_results_to_minutes(results)
##  File "C:\Users\Devlab\Desktop\Dt\Scrap\test_1.py", line 99, in convert_results_to_minutes
##    results[a]=int(string_holder[:string_holder.index('minute')])
##ValueError: invalid literal for int() with base 10: '1 hour, 13 '
