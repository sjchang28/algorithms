# Python3 program to perform basic insertionSort

DEFAULT_FOLDER = "./out/insertionsort/"
DEFAULT_SDFOLDER = DEFAULT_FOLDER+"sorted_data/"
DEFAULT_RCFOLDER = DEFAULT_FOLDER+"Run Time Complexity/"

import os,errno
from sys import argv
from gzip import open as gopen
from datetime import datetime as dt
from datetime import timedelta
from glob import glob
from time import process_time
from matplotlib.pyplot import plot,scatter,ylabel,xlabel,title,savefig,clf

epoch = dt(1970,1,1)
tdSeconds = timedelta(seconds=1)

def updateEpochTz(utc_time):
    global epoch
    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=utc_time.tzinfo)    
    else:
        assert False
def timestamp_ms(utc_time):
    global epoch
    if epoch.tzinfo != utc_time.tzinfo:
        updateEpochTz(utc_time)
    td = (utc_time - epoch) / tdSeconds
    return int(td) #(td.days * 86400 + td.seconds) * 10**6 + td.microseconds
def convert2time(line):
    dateString = line.split(' ')[0]
    dateString = dateString[:-3] + dateString[-2:]
    utc_time = dt.strptime(dateString,'%Y-%m-%dT%H:%M:%S%z')
    return timestamp_ms(utc_time=utc_time)
def datetimeComparison(key,index):
    dateKey = convert2time(key)
    dateIndex = convert2time(index)
    return True if dateKey < dateIndex else False

# Post Processing Functions
def plotGraph(dataset,runTimes):
    folderSize = sorted(runTimes.keys())
    runTimeComplexity = [runTimes[key] for key in folderSize]

    scatter(folderSize,runTimeComplexity)
    plot(folderSize,runTimeComplexity)
    xlabel("File Size (lines)")
    ylabel("Run Time (s)")
    title("Run Time Complexity")
    savefig(DEFAULT_RCFOLDER+"Run Time Complexity For InsertionSort on Dataset "+dataset)
    clf()
def write2File(filename,keyList,dataMap): # Write sorted file from unsorted data
    outDirectory = os.path.dirname(filename)
    try:
        os.makedirs(outDirectory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with gopen(filename,"wt",encoding="latin-1") as fout:
        for i in range(0,len(keyList)):
            for line in dataMap[keyList[i]]:
                fout.write(line)
def writeRunComplexity2File(dataset,runTimes): # Save run complexity of each file
    orderedKeys = sorted(runTimes.keys())
    with open(DEFAULT_RCFOLDER+"logs/runtimes_"+dataset+".bin","wb+") as f:
        for key in orderedKeys:
            req = str(key)+","+str(runTimes[key])+"," + dt.now().strftime("%Y-%m-%dT%H:%M:%S%z")+"\n"
            res = bytes(req,"utf-8")
            f.write(res)

def getData(filename):
    keyList = []
    dataMap = {}
    prevKey = 0
    with gopen(filename,"rt",encoding="latin-1") as fin:
        lineNums = 0
        for line in fin:
            s = line
            try:
                key = convert2time(s)
            except ValueError:
                key = prevKey
            if key not in dataMap.keys():
                dataMap[key] = []
                keyList.append(key)
            dataMap[key].append(line)
            lineNums += 1
            prevKey = key
    return keyList,dataMap,lineNums

def insertionSort(arr):
    for i in range(1,len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr

def sortData(dataset,repeatValue=5):
	runTimes = dict()
	for file in glob(dataset+"**/*.gz"):
		print("InsertionSort::File "+file)
		lineNums = 0
		for i in range(repeatValue):
			keyList,dataMap,lineNums = getData(file)

			# Driver Function for InsertionSort + Timings
			startTime = process_time()
			insertionSort(arr=keyList)
			write2File(filename=DEFAULT_SDFOLDER+file,keyList=keyList,dataMap=dataMap)
			endTime = process_time()

			totalTime = endTime - startTime
			print("+ ("+str(i+1)+"/"+str(repeatValue)+") "+str(totalTime))
			runTimes[lineNums] = (runTimes[lineNums] + totalTime) if lineNums in runTimes.keys() else totalTime
		runTimes[lineNums] /= repeatValue
	plotGraph(dataset,runTimes)
	writeRunComplexity2File(dataset,runTimes)

if __name__ == "__main__":
    # python3 insertionsort.py A 5
    sortData(argv[1],int(argv[2]))
    