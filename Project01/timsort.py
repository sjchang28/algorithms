''' -------------------------------------------------------------------------- '''
'''                                 TimSort                                    '''
''' -------------------------------------------------------------------------- '''

MIN_MERGE = 32
SORTINGMODE = "TimSort"
DATASET_FOLDER = "./datasets/"
DEFAULT_FOLDER = "./analysis/timsort/"
DEFAULT_SDFOLDER = DEFAULT_FOLDER+"sorted_data/"
DEFAULT_RCFOLDER = DEFAULT_FOLDER+"runtime_complexity/"
WARMUP_VALUE = 5

LOADTIME = 0
SORTTIME = 1
WRITETIME = 2

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
    return int(td) # (td.days * 86400 + td.seconds) * 10**6 + td.microseconds
def convert2time(line):
    dateString = line.split(' ')[0]
    dateString = dateString[:-3] + dateString[-2:]
    dateTime = dt.strptime(dateString,'%Y-%m-%dT%H:%M:%S%z')
    return dateTime
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
def validateSort(unsortedKeyList,keyList): # Validate Sort
    sortedKeyList = sorted(unsortedKeyList)
    if sortedKeyList != keyList:
        print("  ✘ Invalid "+SORTINGMODE)
        exit()
def plotGraph(dataset,runTimes):
    folderSize = sorted(runTimes[SORTTIME].keys())
    runTimeComplexity = [(runTimes[SORTTIME][key] + runTimes[WRITETIME][key]) for key in folderSize]

    scatter(folderSize,runTimeComplexity)
    plot(folderSize,runTimeComplexity)
    xlabel("File Size (lines)")
    ylabel("Run Time (s)")
    title("Run Time Complexity")
    savefig(DEFAULT_RCFOLDER+"Run Time Complexity for "+SORTINGMODE+" on Dataset "+dataset)
    clf()
def writeSortingData2File(dataset,lineNums,runTimes): # Save sorting data of each file
    orderedKeys = sorted(runTimes[LOADTIME].keys())
    with open(DEFAULT_RCFOLDER+"logs/runtimes_"+dataset+".bin","wb+") as f:
        plainheader = "Total Lines,Unique Times,Load Time,Sort Time,Write Time,Total Time,Date+Time\n"
        byteheader = bytes(plainheader,"utf-8")
        f.write(byteheader)
        for key in orderedKeys:
            plaintext = str(lineNums)+","+str(key)+","+str(runTimes[LOADTIME][key])+"," +str(runTimes[SORTTIME][key])+","+str(runTimes[WRITETIME][key])+","+str(runTimes[LOADTIME][key]+runTimes[SORTTIME][key])+","+dt.now().strftime("%Y-%m-%dT%H:%M:%S%z")+"\n"
            bytetext = bytes(plaintext,"utf-8")
            f.write(bytetext)


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
def sortData(dataset,repeatValue=10):
    print("LDT:Loading Data Time | SDT:Sorting Data Time | WDT:Writing Data Time")
    runTimes = [{},{},{}]
    for file in glob(DATASET_FOLDER+dataset+"**/*.gz"):
        print(SORTINGMODE+"::File "+file)
        for i in range(repeatValue + WARMUP_VALUE): # Repeat Value (5-10) + Warm-Ups (5)
            lineNums = 0
            startLoadTime,endLoadTime,totalLoadTime = 0,0,0
            startSortTime,endSortTime,totalSortTime = 0,0,0
            startWriteTime,endWriteTime,totalWriteTime = 0,0,0

            # Read in Data + Convert Time to Int
            startLoadTime = process_time()
            keyList,dataMap,lineNums = getData(file)
            unsortedKeyList = keyList
            endLoadTime = process_time()
            totalLoadTime = endLoadTime - startLoadTime
            
            # Driver Function for TimSort
            startSortTime = process_time()
            timSort(arr=keyList)
            writeSorts2File(filename=DEFAULT_SDFOLDER+file,keyList=keyList,dataMap=dataMap)
            endSortTime = process_time()
            totalSortTime = endSortTime - startSortTime

	    # Write Sorted Data
            startWriteTime = process_time()
            writeSorts2File(filename=DEFAULT_SDFOLDER+file,keyList=keyList,dataMap=dataMap)
            endWriteTime = process_time()
            totalWriteTime = endWriteTime - startWriteTime

            validateSort(unsortedKeyList,keyList)
            if i >= WARMUP_VALUE:
                print("  ("+str(i-(WARMUP_VALUE-1))+"/"+str(repeatValue)+").....{:.5f}s".format(totalSortTime+totalWriteTime)+"/{:.5f}s".format(totalLoadTime+totalSortTime+totalWriteTime)+" [LDT:{:.5f}s".format(totalLoadTime)+" + SDT:{:.5f}s + ".format(totalSortTime)+"WDT:{:.5f}s]".format(totalWriteTime))
                runTimes[LOADTIME][len(keyList)] = (runTimes[LOADTIME][len(keyList)] + totalLoadTime) if len(keyList) in runTimes[LOADTIME].keys() else totalLoadTime
                runTimes[SORTTIME][len(keyList)] = (runTimes[SORTTIME][len(keyList)] + totalSortTime) if len(keyList) in runTimes[SORTTIME].keys() else totalSortTime
                runTimes[WRITETIME][len(keyList)] = (runTimes[WRITETIME][len(keyList)] + totalWriteTime) if len(keyList) in runTimes[WRITETIME].keys() else totalWriteTime

        runTimes[LOADTIME][len(keyList)] /= repeatValue
        runTimes[SORTTIME][len(keyList)] /= repeatValue
        runTimes[WRITETIME][len(keyList)] /= repeatValue
    plotGraph(dataset,runTimes)
    writeSortingData2File(dataset,lineNums,runTimes)

if __name__ == "__main__":
    # python3 timsort.py A 5
    sortData(argv[1],int(argv[2]))