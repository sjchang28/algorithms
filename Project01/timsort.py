# Python3 program to perform basic timSort
import sys
import gzip
import datetime
import glob
import time
import re
import matplotlib.pyplot as plt

MIN_MERGE = 32


def calcMinRun(n):
	"""Returns the minimum length of a
	run from 23 - 64 so that
	the len(array)/minrun is less than or
	equal to a power of 2.

	e.g. 1=>1, ..., 63=>63, 64=>32, 65=>33,
	..., 127=>64, 128=>32, ...
	"""
	r = 0
	while n >= MIN_MERGE:
		r |= n & 1
		n >>= 1
	return n + r


def convert_to_time(line):

	# print(line)
	date_string = line.split(' ')[0]
	date_string = date_string[:-3] + date_string[-2:]
	# print(datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z'))

	return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')


def datetime_comparison(left, right, operator):

	date_time1 = convert_to_time(left)
	date_time2 = convert_to_time(right)

	if operator == '<':
		if date_time1 < date_time2:
			return True
	elif operator == '<=':
		if date_time1 <= date_time2:
			return True

	return False


# This function sorts array from left index to
# to right index which is of size atmost RUN
def insertionSort(arr, left, right):
	for i in range(left + 1, right + 1):
		j = i
		# while j > left and arr[j] < arr[j - 1]:
		while j > left and datetime_comparison(arr[j], arr[j - 1], '<'):
			arr[j], arr[j - 1] = arr[j - 1], arr[j]
			j -= 1


# Merge function merges the sorted runs
def merge(arr, l, m, r):
	
	# original array is broken in two parts
	# left and right array
	len1, len2 = m - l + 1, r - m
	left, right = [], []
	for i in range(0, len1):
		left.append(arr[l + i])
	for i in range(0, len2):
		right.append(arr[m + 1 + i])

	i, j, k = 0, 0, l
	
	# after comparing, we merge those two array
	# in larger sub array
	while i < len1 and j < len2:
		# if left[i] <= right[j]:
		if datetime_comparison(left[i], right[j], '<='):
			arr[k] = left[i]
			i += 1

		else:
			arr[k] = right[j]
			j += 1

		k += 1

	# Copy remaining elements of left, if any
	while i < len1:
		arr[k] = left[i]
		k += 1
		i += 1

	# Copy remaining element of right, if any
	while j < len2:
		arr[k] = right[j]
		k += 1
		j += 1


# Iterative Timsort function to sort the
# array[0...n-1] (similar to merge sort)
def timSort(arr):
	n = len(arr)
	minRun = calcMinRun(n)
	
	# Sort individual subarrays of size RUN
	for start in range(0, n, minRun):
		end = min(start + minRun - 1, n - 1)
		insertionSort(arr, start, end)

	# Start merging from size RUN (or 32). It will merge
	# to form size 64, then 128, 256 and so on ....
	size = minRun
	while size < n:
		
		# Pick starting point of left sub array. We
		# are going to merge arr[left..left+size-1]
		# and arr[left+size, left+2*size-1]
		# After every merge, we increase left by 2*size
		for left in range(0, n, 2 * size):

			# Find ending point of left sub array
			# mid+1 is starting point of right sub array
			mid = min(n - 1, left + size - 1)
			right = min((left + 2 * size - 1), (n - 1))

			# Merge sub array arr[left.....mid] &
			# arr[mid+1....right]
			if mid < right:
				merge(arr, left, mid, right)

		size = 2 * size


def plot_graph(run_times, folder_name):

	x = sorted(run_times.keys())
	y = [run_times[key] for key in x]

	plt.plot(x, y)

	# naming the x axis
	plt.xlabel('File Size')
	# naming the y axis
	plt.ylabel('Run Time')

	# giving a title to my graph
	plt.title('Run Time Complexity')

	plt.savefig('Run Time Complexity For TimSort on Dataset ' + folder_name)
	# function to show the plot
	plt.show()


def sort_data(folder_name, repeat_value):
	# print(os.getcwd() + "\\" + folder_name + "\\")
	# path = folder_name
	files = [f for f in glob.glob(folder_name + "**/*.gz", recursive=True)]
	run_times = {}

	for i in range(repeat_value):
		for file in files:
			# print(file)
			with gzip.open(file, 'rt', encoding="latin-1") as f_in:
				# arr = f_in.readlines()
				# print(arr[:2])
				# print(data)
				arr = re.findall(r'2015.*\n', f_in.read())
				# print(len(match))
				# print(len(arr))
				# file_lengths.append(len(arr))

				start_time = time.process_time()
				timSort(arr)
				end_time = time.process_time()
				print("Process time", end_time - start_time)

				# print(arr[:2])
				if len(arr) in run_times.keys():
					run_times[len(arr)] += end_time - start_time
				else:
					run_times[len(arr)] = end_time - start_time

	for key in run_times.keys():
		run_times[key] = run_times[key]/repeat_value

	plot_graph(run_times, folder_name)


# Driver program to test above function
if __name__ == "__main__":

	# arr = [-2, 7, 15, -14, 0, 15, 0, 7, -7, -4, -13, 5, 8, -14, 12]
	#
	# print("Given Array is")
	# print(arr)

	sort_data(sys.argv[1], int(sys.argv[2]))
	# Function Call
	# timSort(arr)

	# print("After Sorting Array is")
	# print(arr)
	# [-14, -14, -13, -7, -4, -2, 0, 0, 5, 7, 7, 8, 12, 15, 15]
