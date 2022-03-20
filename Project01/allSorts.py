from insertionsort import sortData as ISD
from mergesort import sortData as MSD
from timsort import sortData as TSD

for dataset in ["A","B","C"]:
    ISD(dataset=dataset)
    MSD(dataset=dataset)
    TSD(dataset=dataset)
