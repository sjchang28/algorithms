from insertionsort import sortData as insertionsort
from mergesort import sortData as mergesort
from timsort import sortData as timsort

def allSorts(repeatValue=10):
	for dataset in ["A","B","C"]:
		insertionsort(dataset=dataset,repeatValue=repeatValue)
		mergesort(dataset=dataset,repeatValue=repeatValue)
		timsort(dataset=dataset,repeatValue=repeatValue)

if __name__ == "__main__":
	allSorts()
