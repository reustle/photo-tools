import os
import sys
import pprint

def find_single_raws(path, remove_files=False):
	""" Find all RAW files with no matching JPG """
	
	single_raws = []
	
	# Get all filenames in the given dir
	dir_list = os.listdir(path)
	
	# Convert all filenames to lowercase
	dir_list_lower = [x.lower() for x in dir_list]
	
	for filename in dir_list:
		split_filename = filename.split('.')
		
		if len(split_filename) == 1:
			# Filename doesn't have an extension
			continue
		
		if len(split_filename) > 2:
			# Filename has more than 1 period
			continue
		
		if split_filename[1].lower() == 'nef':
			# We're on a RAW file
			
			if split_filename[0].lower() + '.jpg' in dir_list_lower:
				# Found matching jpg
				continue
			
			elif split_filename[0].lower() + '.jpeg' in dir_list_lower:
				# Found matching jpeg
				continue
			
			else:
				# Didn't find matching jpg
				single_raws.append(path + '.'.join(split_filename))
	
	if remove_files:
		for filename in single_raws:
			os.remove(filename)
			
		return True
	else:
		print('# READONLY MODE')
		for filename in single_raws:
			print(filename)
		
		print('# Will remove ' + str(len(single_raws)) + ' of ' + str(len(dir_list_lower)) + ' files')
	
	return sorted(single_raws)

if __name__ == '__main__':
	""" Do it """
	
	args_list = sys.argv
	if args_list[0] == 'python':
		args_list = args_list[1:]
	
	
	if len(args_list) > 1:
		if len(args_list) >= 3:
			# Pass README as 2nd arg to use readonly mode
			
			find_single_raws(args_list[1], remove_files=False)
		else:
			find_single_raws(args_list[1], remove_files=True)
	else:
		print('Needs path to image dir')

