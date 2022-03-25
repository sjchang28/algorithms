from insertionsort import sortData as ISD
from mergesort import sortData as MSD
from timsort import sortData as TSD

def allSorts(repeatValue=10):
	for dataset in ["A","B","C"]:
		ISD(dataset=dataset,repeatValue=repeatValue)
		MSD(dataset=dataset,repeatValue=repeatValue)
		TSD(dataset=dataset,repeatValue=repeatValue)

if __name__ == "__main__":
	allSorts()
