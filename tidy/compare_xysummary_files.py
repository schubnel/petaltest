# compare two summary files
# check if they are identical. if not write out difference
# we are interested in files for the same positioner


import pandas as pd
import glob

def create_file_list(path,fname):
	"""
	creates an ordered list of files with absolute path
	"""
	return sorted(glob.glob(path+'/'+fname+'_summary.csv'))

def read_start_dates_from_summary(filename):
	"""
		read a summary file into a pandas dataframe and put start dates into a list. list is returned
	"""
	df = pd.read_csv(filename) # create data frame
	# make sure 'start time is a column'
	header=list(df)
	if "start time" not in header: 
		print("File integrity problem: start time not found in header! ")
		return False
	# get a list of start times
	return df["start time"]

def compare(xysummary_file1, xysummary_file2):
	start_list1=read_start_dates_from_summary(xysummary_file1)
	start_list2=read_start_dates_from_summary(xysummary_file2)

	if list(start_list1) == list(start_list2):
		print("Files are identical")
		return []
	if set(start_list1) == set(start_list2):
		print("Files are identical but start date order is not")
		return []

	in2_not1=[elem for elem in start_list2 if elem not in start_list1]	
	in1_not2=[elem for elem in start_list1 if elem not in start_list2]

	if in1_not2 != []:
		print(" In "+xysummary_file1+" only: ")
		print(in1_not2)
	if in2_not1 != []:
		print(" In "+xysummary_file2+" only: ")
		print(in2_not1)
	return 	in1_not2,in2_not1


if __name__=='__main__':
	import sys
	if len(sys.argv) < 4:
		print ("Not enough arguments. Two are needed.")


	flist1=create_file_list(sys.argv[1],sys.argv[3])
	flist2=create_file_list(sys.argv[2],sys.argv[3])	

	compare(flist1,flist2)










