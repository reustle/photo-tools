import os
import sys
import time
import Image
import random
import ExifTags
from pprint import pprint


def rename_files(path, ADD_TIME_SHIFT=False):
	""" Takes in a directory and renames files to their creation time """
	
	allowed_extensions = ['jpg', 'jpeg', 'mp4', 'mov']
	
	# Make sure the path has a trailing slash
	if path[-1] != '/':
		path = path + '/'

	# Get all filenames in the given dir
	dir_list = os.listdir(path)
	
	# Grab all jpgs from that list
	file_list = []
	for filename in dir_list:
		split_filename = filename.lower().split('.')
		if len(split_filename) > 1 and split_filename[1] in allowed_extensions:
			file_list.append(path + filename)
	
	
	# Rename Files
	new_filenames = []
	for filename in file_list:
		
		# Compile current file details
		extension = filename.lower().split('.')[-1]
		path = os.path.split(filename)[0] + '/'
		
		# If it is an image, read the EXIF data
		# otherwise, fall back to file creation time
		if extension == 'jpg' and not ADD_TIME_SHIFT:
			# Open the image for reading
			img = Image.open(filename)
			
			# Load the EXIF data
			this_exif = img._getexif()
			if not this_exif:
				continue
			
			# Pull out created_time
			exif = dict(this_exif.items())
			created_time = exif.get(36867)
			
		else:
			# Fall back to mtime
			created_time = float(os.path.getmtime(filename))
			
			if ADD_TIME_SHIFT:
				created_time += 3600 * ADD_TIME_SHIFT
			
			created_time = time.strftime('%Y%m%d-%H%M%S', time.localtime(created_time))
		
		# Generate new filename
		created_time = created_time.replace(' ', '-').replace(':','')
		new_filename = created_time + '.' + extension
		
		# Keep track of our new filenames, incase we need have duplicates
		if new_filename in new_filenames:
			print new_filename + ' already exists'
			new_filename += '-' + str(random.randint(100,999))
		
		new_filenames.append(new_filename)
		
		# Print notification
		if False:
			old_filename = filename.replace(path, '')
			print( '{0} => {1}'.format(old_filename, new_filename) )
			continue
		
		# Generate new filename
		new_full_filename = path + new_filename
		
		# See if that file exists
		is_file = os.path.isfile(new_full_filename)
		if is_file:
			print(new_full_filename + ' already exists, adding random num')
			new_full_filename += '-' + str(random.randint(100,999))
		
		# Rename the file
		os.rename(filename, new_full_filename)
		
if __name__ == '__main__':
	""" Takes a directory, and renames files (jpg, mov, mp4) to use timestamp """
	
	if len(sys.argv) > 1:
		
		if len(sys.argv) > 3 and sys.argv[2] == '--time-shift':
			try:
				offset = float(sys.argv[3])
				print('Offset set to {0}'.format(offset))
			except:
				print('Invalid Offset')
			
			rename_files(sys.argv[1], ADD_TIME_SHIFT=offset)
		else:
			rename_files(sys.argv[1])
			
	else:
		print('Needs path to image dir. Use like timestamp_filenames.py /foo/bar/ --time-shift 12')
	
