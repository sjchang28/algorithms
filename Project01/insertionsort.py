''' -------------------------------------------------------------------------- '''
'''                              InsertionSort                                 '''
''' -------------------------------------------------------------------------- '''

import errno
import os
from matplotlib.pyplot import plot, scatter, ylabel, xlabel, title, savefig, clf
from time import process_time
from glob import glob
from datetime import timedelta
from datetime import datetime as dt
from gzip import open as gzopen
from sys import argv, exit
SORTINGMODE = "InsertionSort"
DATASET_FOLDER = "./datasets/"
DEFAULT_FOLDER = "./analysis/insertionsort/"
DEFAULT_SDFOLDER = DEFAULT_FOLDER+"sorted_data/"
DEFAULT_RCFOLDER = DEFAULT_FOLDER+"runtime_complexity/"
WARMUP_VALUE = 5

LOADTIME = 0
SORTTIME = 1
WRITETIME = 2


''' -------------------------- Pre-Process Functions ------------------------- '''
epoch = dt(1970, 1, 1)
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
    return int(td) 
def convert2time(line):
    dateString = line.split(' ')[0]
    dateString = dateString[:-3] + dateString[-2:]
    return dt.strptime(dateString, '%Y-%m-%dT%H:%M:%S%z')
def getData(filename):
    keyList = []
    dataMap = {}
    prevKey = 0
    with gzopen(filename, "rt", encoding="latin-1") as fin:
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
    return keyList, dataMap, lineNums


''' ------------------------- Post-Process Functions ------------------------- '''
def writeSorts2File(filename, keyList, dataMap):  # Write sorted file from unsorted data
    outDirectory = os.path.dirname(filename)
    try:
        os.makedirs(outDirectory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with gzopen(filename, "wt", encoding="latin-1") as fout:
        for i in range(0, len(keyList)):
            for line in dataMap[keyList[i]]:
                fout.write(line)
def validateSort(unsortedKeyList, keyList):  # Validate Sort
    sortedKeyList = sorted(unsortedKeyList)
    if sortedKeyList != keyList:
        print("  ✘ Invalid "+SORTINGMODE)
        exit()
def plotGraph(dataset, runTimes):
    folderSize = sorted(runTimes[SORTTIME].keys())
    runTimeComplexity = [((runTimes[SORTTIME][key] + runTimes[WRITETIME][key]) * 1000) for key in folderSize]

    scatter(folderSize, runTimeComplexity)
    plot(folderSize, runTimeComplexity)
    xlabel("File Size (lines)")
    ylabel("Run Time (ms)")
    title("Run Time Complexity")
    savefig(DEFAULT_RCFOLDER+"Run Time Complexity for "+SORTINGMODE+" on Dataset "+dataset)
    clf()
def writeSortingData2File(dataset, lineNums, runTimes): # Save sorting data of each file
    orderedKeys = sorted(runTimes[LOADTIME].keys())
    with open(DEFAULT_RCFOLDER+"logs/runtimes_"+dataset+".bin", "wb+") as f:
        plainheader = "Total Lines,Unique Times,Load Time,Sort Time,Write Time,Total Time,Date+Time\n"
        byteheader = bytes(plainheader, "utf-8")
        f.write(byteheader)
        for key in orderedKeys:
            plaintext = str(lineNums)+","+str(key)+","+str(runTimes[LOADTIME][key])+","+str(runTimes[SORTTIME][key])+","+str(runTimes[WRITETIME][key])+","+str(runTimes[LOADTIME][key]+runTimes[SORTTIME][key]+runTimes[WRITETIME][key])+","+dt.now().strftime("%Y-%m-%dT%H:%M:%S%z")+"\n"
            bytetext = bytes(plaintext, "utf-8")
            f.write(bytetext)


''' ------------------------- Driving Sort Functions ------------------------- '''
# InsertionSort | https://www.geeksforgeeks.org/insertion-sort/
def insertionSort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and key < arr[j]:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr
def sortData(dataset, repeatValue=10):
    print("Progress.....TotalDataTime   LoadingDataTime   SortingDataTime   WritingDataTime")
    runTimes = [{}, {}, {}]
    for file in glob(DATASET_FOLDER+dataset+"**/*.gz"):
        print(SORTINGMODE+"::File "+file)
        for i in range(repeatValue + WARMUP_VALUE):  # Repeat Value (5-10) + Warm-Ups (5)
            lineNums = 0
            startLoadTime, endLoadTime, totalLoadTime = 0, 0, 0
            startSortTime, endSortTime, totalSortTime = 0, 0, 0
            startWriteTime, endWriteTime, totalWriteTime = 0, 0, 0

            # Read in Data + Convert Time to Int
            startLoadTime = process_time()
            keyList, dataMap, lineNums = getData(file)
            unsortedKeyList = keyList
            endLoadTime = process_time()
            totalLoadTime = endLoadTime - startLoadTime

            # Driver Function for InsertionSort
            startSortTime = process_time()
            insertionSort(arr=keyList)
            endSortTime = process_time()
            totalSortTime = endSortTime - startSortTime

            # Write Sorted Data
            startWriteTime = process_time()
            writeSorts2File(filename=DEFAULT_SDFOLDER+file,keyList=keyList, dataMap=dataMap)
            endWriteTime = process_time()
            totalWriteTime = endWriteTime - startWriteTime

            validateSort(unsortedKeyList, keyList)
            if i >= WARMUP_VALUE:
                if (i-(WARMUP_VALUE-1)) >= 10:
                    print("  ("+str(i-(WARMUP_VALUE-1))+"/"+str(repeatValue)+")....{:.5f}s".format(totalLoadTime+totalSortTime+totalWriteTime)+"   {:.5f}s".format(totalLoadTime)+"   {:.5f}s".format(totalSortTime)+"   {:.5f}s".format(totalWriteTime))
                else:
                    print("  ("+str(i-(WARMUP_VALUE-1))+"/"+str(repeatValue)+").....{:.5f}s".format(totalLoadTime+totalSortTime+totalWriteTime)+"   {:.5f}s".format(totalLoadTime)+"   {:.5f}s".format(totalSortTime)+"   {:.5f}s".format(totalWriteTime))
                runTimes[LOADTIME][len(keyList)] = (runTimes[LOADTIME][len(keyList)] + totalLoadTime) if len(keyList) in runTimes[LOADTIME].keys() else totalLoadTime
                runTimes[SORTTIME][len(keyList)] = (runTimes[SORTTIME][len(keyList)] + totalSortTime) if len(keyList) in runTimes[SORTTIME].keys() else totalSortTime
                runTimes[WRITETIME][len(keyList)] = (runTimes[WRITETIME][len(keyList)] + totalWriteTime) if len(keyList) in runTimes[WRITETIME].keys() else totalWriteTime

        runTimes[LOADTIME][len(keyList)] /= repeatValue
        runTimes[SORTTIME][len(keyList)] /= repeatValue
        runTimes[WRITETIME][len(keyList)] /= repeatValue
    plotGraph(dataset, runTimes)
    writeSortingData2File(dataset, lineNums, runTimes)


if __name__ == "__main__":
    # python3 insertionsort.py A 5
    sortData(argv[1], int(argv[2]))
