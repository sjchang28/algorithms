# Python3 program to perform basic insertionSort
from cProfile import run
from curses import pair_content
from sys import argv
from gzip import open
from datetime import datetime as dt
from glob import glob
from time import process_time
from re import findall
from matplotlib.pyplot import plot, scatter, ylabel, xlabel, title, savefig, clf

def convert2time(line):
	dateString = line.split(' ')[0]
	dateString = dateString[:-3] + dateString[-2:]
	return dt.strptime(dateString,'%Y-%m-%dT%H:%M:%S%z')
def datetimeComparison(key,index):
	dateKey = convert2time(key)
	dateIndex = convert2time(index)
	return True if dateKey < dateIndex else False
def plotGraph(dataset,runTimes):
	folderSize = sorted(runTimes.keys())
	runTimeComplexity = [runTimes[key] for key in folderSize]

	scatter(folderSize,runTimeComplexity)
	plot(folderSize,runTimeComplexity)
	xlabel("File Size (lines)")
	ylabel("Run Time (s)")
	title("Run Time Complexity")
	savefig("./Run Time Complexity/Run Time Complexity For Insertion Sort on Dataset "+dataset)
	clf()

# https://www.geeksforgeeks.org/insertion-sort/
def insertionSort(arr):
	for i in range(1, len(arr)):
		key = arr[i]
		j = i-1
		while j >= 0 and datetimeComparison(key,arr[j]):
			arr[j+1] = arr[j]
			j -= 1
		arr[j+1] = key
def sortData(datase,repeatValue=5):
	for dataset in ["A","B","C"]:
		runTimes = dict()
		for file in glob(dataset+"**/*.gz"):
			print("File "+file)
			for i in range(repeatValue):
				with open(file,"rt",encoding="latin-1") as f:
					arr = findall(r"2015.*\n",f.read())

					# Driver Function for Insertion Sort + Timings
					startTime = process_time()
					insertionSort(arr)
					endTime = process_time()

					totalTime = endTime - startTime
					print("+ ("+str(i+1)+"/"+str(repeatValue)+") "+str(totalTime))
					runTimes[len(arr)] = (runTimes[len(arr)] + totalTime) if len(arr) in runTimes.keys() else totalTime
			runTimes[key] /= repeatValue
			orderedKeys = sorted(runTimes.keys())
			with open("./Run Time Complexity/logs/runtimes_"+dataset+".bin","ab+") as f:
				for key in orderedKeys:
					req = str(key)+","+str(runTimes[key])+","+dt.now.strftime("%Y-%m-%dT%H:%M:%S%z")+"\n"
					res = bytes(req,'utf-8')
					f.write(res)
		plotGraph(dataset,runTimes)

if __name__ == "__main__":
	# python3 insertionsort.py A 5
	sortData(argv[1],int(argv[2]))
