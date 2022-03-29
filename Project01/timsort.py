''' -------------------------------------------------------------------------- '''
'''                                 TimSort                                    '''
''' -------------------------------------------------------------------------- '''

SORTINGMODE = "TimSort"
DATASET_FOLDER = "./datasets/"
DEFAULT_FOLDER = "./analysis/timsort/"
DEFAULT_RCFOLDER = DEFAULT_FOLDER+"runtime_complexity/"
MIN_MERGE = 32
WARMUP_VALUE = 5

# Index in Run Time Dictionary
UNIQUEKEYS = 0
LOADTIME = 1
SORTTIME = 2
WRITETIME = 3

import errno
import os
from matplotlib.pyplot import plot, scatter, ylabel, xlabel, title, savefig, clf
from time import process_time
from glob import glob
from datetime import timedelta
from datetime import datetime as dt
from gzip import open as gzopen
from sys import argv, exit
import csv


''' -------------------------- Pre-Process Functions ------------------------- '''
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
def plotGraph(dataset, runtimes):
    orderedKeys = sorted(runtimes[UNIQUEKEYS].keys())
    folderSize = [runtimes[UNIQUEKEYS][key] for key in orderedKeys]
    runtimeComplexity = [((runtimes[SORTTIME][key] + runtimes[WRITETIME][key]) * 1000) for key in orderedKeys]

    scatter(folderSize, runtimeComplexity)
    plot(folderSize, runtimeComplexity)
    xlabel("File Size (lines)")
    ylabel("Run Time (ms)")
    title("Run Time Complexity for "+SORTINGMODE)
    savefig(DEFAULT_RCFOLDER+"Run Time Complexity for "+SORTINGMODE+" on Dataset "+dataset)
    clf()
def writeSortingData2File(dataset, runtimes): # Save sorting data of each file
    orderedKeys = sorted(runtimes[UNIQUEKEYS].keys())
    with open(DEFAULT_RCFOLDER+"logs/runtimes:"+dataset+".csv", "w+") as f:
        writer = csv.writer(f)
        writer.writerow(["Total Lines","Unique Lines","Load Time","Sort Time","Write Time","Total Time","Sort+Write Time","Date+Time"])
        for key in orderedKeys:
            writer.writerow([key,runtimes[UNIQUEKEYS][key],runtimes[LOADTIME][key],runtimes[SORTTIME][key],runtimes[WRITETIME][key],(runtimes[LOADTIME][key]+runtimes[SORTTIME][key]+runtimes[WRITETIME][key]),(runtimes[SORTTIME][key]+runtimes[WRITETIME][key]),dt.now().strftime("%Y-%m-%dT%H:%M:%S%z")])


''' ------------------------- Driving Sort Functions ------------------------- '''
# TimSort | https://www.geeksforgeeks.org/timsort/
def calcMinRun(n):
    r = 0
    while n >= MIN_MERGE:
        r |= n & 1
        n >>= 1
    return n + r
def insertion(arr, left, right):
    for i in range(left + 1, right + 1):
        j = i
        while j > left and arr[j] < arr[j - 1]:
            arr[j], arr[j - 1] = arr[j - 1], arr[j]
            j -= 1
def merge(arr, l, m, r):
    len1, len2 = m - l + 1, r - m
    left, right = [], []
    for i in range(0, len1):
        left.append(arr[l + i])
    for i in range(0, len2):
        right.append(arr[m + 1 + i])

    i, j, k = 0, 0, l

    while i < len1 and j < len2:
        if left[i] <= right[j]:
            arr[k] = left[i]
            i += 1
        else:
            arr[k] = right[j]
            j += 1
        k += 1
    while i < len1:
        arr[k] = left[i]
        k += 1
        i += 1
    while j < len2:
        arr[k] = right[j]
        k += 1
        j += 1
def timSort(arr):
    n = len(arr)
    minRun = calcMinRun(n)

    for start in range(0, n, minRun):
        end = min(start + minRun - 1, n - 1)
        insertion(arr, start, end)

    size = minRun
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(n - 1, left + size - 1)
            right = min((left + 2 * size - 1), (n - 1))
            if mid < right:
                merge(arr, left, mid, right)
        size = 2 * size
    return arr
def sortData(dataset, repeatValue=10):
    print("Progress.....TotalDataTime   LoadingDataTime   SortingDataTime   WritingDataTime")
    runtimes = [{}, {}, {}, {}]
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

            # Driver Function for TimSort
            startSortTime = process_time()
            timSort(arr=keyList)
            endSortTime = process_time()
            totalSortTime = endSortTime - startSortTime

            # Write Sorted Data
            startWriteTime = process_time()
            writeSorts2File(filename=DEFAULT_FOLDER+file,keyList=keyList, dataMap=dataMap)
            endWriteTime = process_time()
            totalWriteTime = endWriteTime - startWriteTime

            validateSort(unsortedKeyList, keyList)
            if i >= WARMUP_VALUE:
                if (i-(WARMUP_VALUE-1)) >= 10:
                    print("  ("+str(i-(WARMUP_VALUE-1))+"/"+str(repeatValue)+")....{:.5f}s".format(totalLoadTime+totalSortTime+totalWriteTime)+"   {:.5f}s".format(totalLoadTime)+"   {:.5f}s".format(totalSortTime)+"   {:.5f}s".format(totalWriteTime))
                else:
                    print("  ("+str(i-(WARMUP_VALUE-1))+"/"+str(repeatValue)+").....{:.5f}s".format(totalLoadTime+totalSortTime+totalWriteTime)+"   {:.5f}s".format(totalLoadTime)+"   {:.5f}s".format(totalSortTime)+"   {:.5f}s".format(totalWriteTime))
                runtimes[LOADTIME][lineNums] = (runtimes[LOADTIME][lineNums] + totalLoadTime) if lineNums in runtimes[LOADTIME].keys() else totalLoadTime
                runtimes[SORTTIME][lineNums] = (runtimes[SORTTIME][lineNums] + totalSortTime) if lineNums in runtimes[SORTTIME].keys() else totalSortTime
                runtimes[WRITETIME][lineNums] = (runtimes[WRITETIME][lineNums] + totalWriteTime) if lineNums in runtimes[WRITETIME].keys() else totalWriteTime

        runtimes[UNIQUEKEYS][lineNums] = len(keyList)
        runtimes[LOADTIME][lineNums] /= repeatValue
        runtimes[SORTTIME][lineNums] /= repeatValue
        runtimes[WRITETIME][lineNums] /= repeatValue
    plotGraph(dataset, runtimes)
    writeSortingData2File(dataset, runtimes)


if __name__ == "__main__":
    # python3 timsort.py A 5
    sortData(argv[1], int(argv[2]))
