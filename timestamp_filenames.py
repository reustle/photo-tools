import os
import sys
import time
import random
import datetime
from pprint import pprint
from PIL import Image, ExifTags

def read_directory(path):
	""" Return a list of all images in a dir """
	
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
	
	return file_list

def read_timestamp(filename):
	""" Get the timestamp for a file, either exif or meta data """
	
	# Compile current filename details
	extension = filename.lower().split('.')[-1]
	path = os.path.split(filename)[0] + '/'
	
	# If it is an image, read the EXIF data
	# otherwise, fall back to file creation time
	if extension == 'jpg':
		# Open the image for reading
		img = Image.open(filename)
		
		# Load the EXIF data
		this_exif = img._getexif()
		if not this_exif:
			return None
		
		# Pull out created_time
		exif = dict(this_exif.items())
		created_time = exif.get(36867)
		created_time = datetime.datetime.strptime(created_time, '%Y:%m:%d %H:%M:%S')
		
	else:
		# Fall back to mtime
		created_time = datetime.datetime.fromtimestamp(os.path.getmtime(filename))
	
	return created_time

def rename_files(path, time_shift=None, debug_mode=True):
	""" Takes in a directory and renames files to their creation time """
	
	# Load file list
	file_list = read_directory(path)
	
	# Rename Files
	new_filenames = []
	for filename in file_list:
		
		# Parse timestamp from file
		created_time = read_timestamp(filename)
		if not created_time:
			print('Error parsing timetamp for {0}'.format(filename))
		
		# Apply the time_shift if it exists
		if time_shift:
			created_time = created_time + datetime.timedelta(hours=time_shift)
		
		# Generate the new filename
		extension = filename.lower().split('.')[-1]
		new_filename = '{timestamp}.{extension}'.format(**{
			'timestamp' : created_time.strftime('%Y%m%d-%H%M%S'),
			'extension' : extension,
		})
		
		# Keep track of our new filenames, incase we need have duplicates
		if new_filename in new_filenames:
			# This filename already exists, adding random numbers
			new_filename = '{timestamp}-{randomint}.{extension}'.format(**{
				'timestamp' : created_time.strftime('%Y%m%d-%H%M%S'),
				'randomint' : random.randint(100,999),
				'extension' : extension,
			})
		
		new_filenames.append(new_filename)
		
		# Print notification
		if debug_mode:
			old_filename = filename.replace(path, '')
			print( '{0} => {1}'.format(old_filename, new_filename) )
			continue
		
		# Generate new filename
		new_full_filename = path + new_filename
		
		# See if the filename exists already
		is_file = os.path.isfile(new_full_filename)
		if is_file:
			print(new_full_filename + ' already exists, adding random num')
			new_full_filename += '-' + str(random.randint(100,999))
		
		# Rename the file
		if not debug_mode:
			os.rename(filename, new_full_filename)
		
if __name__ == '__main__':
	""" Takes a directory, and renames media files (jpg, mov, mp4) to use timestamp """
	
	if len(sys.argv) != 2:
		print('Run like: timestamp_filenames.py /photos/dir/')
	
	debug_mode = (raw_input('Debug mode (y/n): ').lower() == 'y')
	time_shift = float(raw_input('Hour offset (eg -4): '))
	
	rename_files(sys.argv[1], time_shift=time_shift, debug_mode=debug_mode)
	
	# Print settings
	print('Finished with offset={offset} and debug={debug}'.format(**{
		'offset' : time_shift,
		'debug' : debug_mode,
	}))
	
