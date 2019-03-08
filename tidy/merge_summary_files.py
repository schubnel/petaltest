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
		Read a summary file into a pandas dataframe and put start dates into a list. 
		The list is returned
	"""
	df = pd.read_csv(filename) # create data frame
	# make sure 'start time is a column'
	header=list(df)
	if "start time" not in header: 
		print("File integrity problem: start time not found in header! ")
		return False
	return df["start time"]

def merge(xysummary_file1, xysummary_file2):
	"""
		Use pandas to concatenate two dataframes, then drop duplicate rows 
		and finally sort by start time
	"""
	m=pd.concat([pd.read_csv(xysummary_file2),pd.read_csv(xysummary_file1)])
	m=m.drop_duplicates()
	m=m.sort_values(by=['start time'],ascending=True)
	return m


def compare(xysummary_file1, xysummary_file2):
	"""
		The comparison between two summary files is made by creating lists of the 'start time'
		columns and comparing those. 
		As an alternative one might just want to compare two pandas dataframes.
	"""
	start_list1=list(read_start_dates_from_summary(xysummary_file1))
	start_list2=list(read_start_dates_from_summary(xysummary_file2))

	if start_list1 == start_list2:
		print("Files are identical")
		return ([],[])
	if set(start_list1) == set(start_list2):
		print("Files are identical but start date order is not")
		return ([],[])

	in2_not1=[elem for elem in start_list2 if elem not in start_list1]	
	in1_not2=[elem for elem in start_list1 if elem not in start_list2]

	if in1_not2 != []:
		print(" In "+xysummary_file1+" only: ")
		print(in1_not2)
	if in2_not1 != []:
		print(" In "+xysummary_file2+" only: ")
		print(in2_not1)
	return 	(in1_not2,in2_not1)

if __name__=='__main__':
	import sys
	import os
	from shutil import copy2 as fcopy
	"""
	Inputs:
		comp1_path: first path to files to be merged
		comp2_path: second path to files to be merged
		merge_path: path to where merged files will be written to
		filename: filename(s) to be compared, wildcard characters are accepted
	"""
	# first we make sure that both comp directories exist. If not exit with error message
	if len(sys.argv) < 4:
		print ("Not enough arguments. Three are needed.")
		exit(1)
	comp1_path=sys.argv[1]
	comp2_path=sys.argv[2]	
	merge_path=sys.argv[3]	
	if not os.path.exists(comp1_path):
		print ('Directory not found: '+comp1_path)
		exit(1)
	if not os.path.exists(comp2_path):
		print ('Directory not found: '+comp2_path)
		exit(1)

	# create merge directory if it doesn't already exist. Exit on error.
	try:
		if not os.path.exists(merge_path):
			os.makedirs(merge_path)
	except:
		print("Could not create merge directory")
		exit(1)

	print(" Directories to compare: ")
	print(comp1_path)
	print(comp2_path)
	print(" Merge directory: ")
	print(merge_path)

	# create a list of all files in comp1 and a list of files in comp2.
	# Print out statistics 

	comp1_list=[os.path.basename(e) for e in sorted(glob.glob(comp1_path+'/'+sys.argv[4]+'*_summary.csv'))]
	comp2_list=[os.path.basename(e) for e in sorted(glob.glob(comp2_path+'/'+sys.argv[4]+'*_summary.csv'))]

	print(" Number of summary files found in "+comp1_path+": "+str(len(comp1_list)))
	print(" Number of summary files found in "+comp2_path+": "+str(len(comp2_list)))

	# files that are only in either comp1 or comp2 are copied to merge directory

	in2_not1=[elem for elem in comp2_list if elem not in comp1_list]	
	in1_not2=[elem for elem in comp1_list if elem not in comp2_list]

	both=[elem for elem in comp1_list if elem in comp2_list]
	# print out statistics

	print(" Number of summary files listed in both directories: "+str(len(both)))
	print(" Number of summary files listed only in "+str(comp1_path)+": "+str(len(in1_not2)))
	print(" Number of summary files listed only in "+str(comp2_path)+": "+str(len(in2_not1)))

	ncop=0
	for file in in1_not2:
		fcopy(os.path.join(comp1_path,file),os.path.join(merge_path,file))
		ncop=ncop+1
	for file in in2_not1:
		fcopy(os.path.join(comp2_path,file),os.path.join(merge_path,file))
		ncop=ncop+1
	print(str(ncop)+" files copied to merge directory")		

# tested and okay until here

	# only files that are in both comp direcories are compared
	# extract filenames from the 'both' list

	for fn in both:
		print ("Checking file: ",fn)
	
		in1_not2,in2_not1=compare(os.path.join(comp1_path,fn),os.path.join(comp2_path,fn))
		
		# if files are identical we copy comp1 to the merge directory

		if in1_not2 == [] and in2_not1 == []:
			print ("copying to merge directory")
			fcopy(os.path.join(comp1_path,fn),os.path.join(merge_path,fn))

		# otherwise we need to merge

		else:
			print ("merging and writing to merge directory")
			m=merge(os.path.join(comp1_path,fn),os.path.join(comp2_path,fn))
			m.to_csv(os.path.join(merge_path,fn),index=False)

	print("exit")
	exit(0)








