# Python3 program to perform basic insertionSort
from sys import argv
from gzip import open
from datetime import datetime as dt
from glob import glob
from time import process_time
from re import findall
from matplotlib.pyplot import plot, scatter, ylabel, xlabel, title, savefig

def convert2time(line):
	dateString = line.split(' ')[0]
	dateString = dateString[:-3] + dateString[-2:]
	return dt.strptime(dateString,'%Y-%m-%dT%H:%M:%S%z')
def datetimeComparison(key,index):
	dateKey = convert2time(key)
	dateIndex = convert2time(index)
	return True if dateKey < dateIndex else False
def insertionSort(arr): # https://www.geeksforgeeks.org/insertion-sort/ 
	for i in range(1, len(arr)):
		key = arr[i]
		j = i-1
		while j >= 0 and datetimeComparison(key,arr[j]):
			arr[j+1] = arr[j]
			j -= 1
		arr[j+1] = key
def plotGraph(folderName,runTimes):
	folderSize = sorted(runTimes.keys())
	runTimeComplexity = [runTimes[key] for key in runTimes]

	scatter(folderSize,runTimeComplexity)
	plot(folderSize,runTimeComplexity)
	xlabel("File Size (lines)")
	ylabel("Run Time (s)")
	title("Run Time Complexity")
	savefig("Run Time Complexity For Insertion Sort on Dataset "+folderName)
	
def sortData(folderName,repeatValue=5):
	for dataset in ["A","B","C"]: # ** replace folderName with dataset
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
		for key in runTimes.keys():
			runTimes[key] /= repeatValue
		plotGraph(dataset,runTimes)
if __name__ == "__main__":
	# python3 insertionsort.py A 5
	sortData(argv[1],int(argv[2]))