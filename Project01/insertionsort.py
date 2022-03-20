''' -------------------------------------------------------------------------- '''
'''                              InsertionSort                                 '''
''' -------------------------------------------------------------------------- '''

SORTINGMODE = "InsertionSort"
DATASET_FOLDER = "./datasets/"
DEFAULT_FOLDER = "./analysis/loadout/insertionsort/"
DEFAULT_SDFOLDER = DEFAULT_FOLDER+"sorted_data/"
DEFAULT_RCFOLDER = DEFAULT_FOLDER+"Run Time Complexity/"

LOAD_TIME = 0
RUN_TIME = 1

import os, errno
from sys import argv, exit
from gzip import open as gzopen
from datetime import datetime as dt
from datetime import timedelta
from glob import glob
from time import process_time
from matplotlib.pyplot import plot, scatter, ylabel, xlabel, title, savefig, clf


''' -------------------------- Pre-Process Functions ------------------------- '''
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
def getData(filename):
    keyList = []
    dataMap = {}
    prevKey = 0
    with gzopen(filename,"rt",encoding="latin-1") as fin:
        lineNums = 0
        for line in fin:
            s = line
            try:
                key = convert2time(s)
            except ValueError:
                key = prevKey
            if key not in dataMap.keys():
                keyList.append(key)
                dataMap[key] = []
            dataMap[key].append(line)
            lineNums += 1
            prevKey = key
    return keyList,dataMap,lineNums


''' ------------------------- Post-Process Functions ------------------------- '''
def validateSort(unsortedKeyList,keyList): # Validate Sort
    sortedKeyList = sorted(unsortedKeyList)
    if sortedKeyList != keyList:
        print("  ✘ Invalid "+SORTINGMODE)
        exit()
def plotGraph(dataset,runTimes):
    folderSize = sorted(runTimes[RUN_TIME].keys())
    runTimeComplexity = [runTimes[key] for key in folderSize]

    scatter(folderSize,runTimeComplexity)
    plot(folderSize,runTimeComplexity)
    xlabel("File Size (lines)")
    ylabel("Run Time (s)")
    title("Run Time Complexity")
    savefig(DEFAULT_RCFOLDER+"Run Time Complexity for "+SORTINGMODE+" on Dataset "+dataset)
    clf()
def writeSorts2File(filename,keyList,dataMap): # Write sorted file from unsorted data
    outDirectory = os.path.dirname(filename)
    try:
        os.makedirs(outDirectory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with gzopen(filename,"wt",encoding="latin-1") as fout:
        for i in range(0,len(keyList)):
            for line in dataMap[keyList[i]]:
                fout.write(line)
def writeSortingData2File(dataset,runTimes): # Save sorting data of each file
    orderedKeys = sorted(runTimes[LOAD_TIME].keys())
    with open(DEFAULT_RCFOLDER+"logs/runtimes_"+dataset+".bin","wb+") as f:
        plainheader = "Total Lines,Load Times, Sort Times,Total Time,Date+Time\n"
        byteheader = bytes(plainheader,"utf-8")
        f.write(byteheader)
        for key in orderedKeys:
            plaintext = str(key)+","+str(runTimes[LOAD_TIME][key])+"," +str(runTimes[RUN_TIME][key])+","+str(runTimes[LOAD_TIME][key]+runTimes[RUN_TIME][key])+","+dt.now().strftime("%Y-%m-%dT%H:%M:%S%z")+"\n"
            bytetext = bytes(plaintext,"utf-8")
            f.write(bytetext)


''' ------------------------- Driving Sort Functions ------------------------- '''
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
    print("LDT:Loading Data Time | SDT:Sorting Data Time")
    runTimes = [{},{}]
    for file in glob(DATASET_FOLDER+dataset+"**/*.gz"):
        print(SORTINGMODE+"::File "+file)
        for i in range(repeatValue):
            lineNums = 0
            startLoadTime,endLoadTime,totalLoadTime = 0,0,0
            startSortTime,endSortTime,totalSortTime = 0,0,0

            # Read in Data + Convert Time to Int
            startLoadTime = process_time()
            keyList,dataMap,lineNums = getData(file)
            unsortedKeyList = keyList
            endLoadTime = process_time()
            totalLoadTime = endLoadTime - startLoadTime
            
            # Driver Function for InsertionSort
            startSortTime = process_time()
            insertionSort(arr=keyList)
            writeSorts2File(filename=DEFAULT_SDFOLDER+file,keyList=keyList,dataMap=dataMap)
            endSortTime = process_time()
            totalSortTime = endSortTime - startSortTime

            validateSort(unsortedKeyList,keyList)
            print("  ("+str(i+1)+"/"+str(repeatValue)+").....{:.5f}s".format(totalLoadTime+totalSortTime)+" [LDT:{:.5f}s".format(totalLoadTime)+" + SDT:{:.5f}s]".format(totalSortTime))
            runTimes[LOAD_TIME][lineNums] = (runTimes[LOAD_TIME][lineNums] + totalLoadTime) if lineNums in runTimes[LOAD_TIME].keys() else totalLoadTime
            runTimes[RUN_TIME][lineNums] = (runTimes[RUN_TIME][lineNums] + totalSortTime) if lineNums in runTimes[RUN_TIME].keys() else totalSortTime
        runTimes[LOAD_TIME][lineNums] /= repeatValue
        runTimes[RUN_TIME][lineNums] /= repeatValue
    plotGraph(dataset,runTimes)
    writeSortingData2File(dataset,runTimes)

if __name__ == "__main__":
    # python3 insertionsort.py A 5
    sortData(argv[1],int(argv[2]))