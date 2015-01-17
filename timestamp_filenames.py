import os
import sys
import time
import Image
import ExifTags
from pprint import pprint


def rename_files(path, ADD_12_HOURS=False):
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
		if extension == 'jpg' and not ADD_12_HOURS:
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
			
			if ADD_12_HOURS:
				created_time += 43200
			
			created_time = time.strftime('%Y%m%d-%H%M%S', time.localtime(created_time))
		
		# Generate new filename
		created_time = created_time.replace(' ', '-').replace(':','')
		new_filename = created_time + '.' + extension
		
		# Keep track of our new filenames, incase we need have duplicates
		if new_filename in new_filenames:
			print new_filename + ' already exists'
			new_filename += '-2'
		
		new_filenames.append(new_filename)
		
		# Rename the file
		new_full_filename = path + new_filename
		
		#print(filename + ' -> ' + new_full_filename)
		os.rename(filename, new_full_filename)
		
if __name__ == '__main__':
	""" Takes a directory, and renames files (jpg, mov, mp4) to use timestamp """
	
	if len(sys.argv) > 1:
		
		if len(sys.argv) > 2 and sys.argv[2] == '--add-12-hours':
			rename_files(sys.argv[1], ADD_12_HOURS=True)
		else:
			rename_files(sys.argv[1])
			
	else:
		print('Needs path to image dir. Use like timestamp_filenames.py /foo/bar/ --ad-12-hours')
	
