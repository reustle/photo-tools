import os
import sys
import time
import Image
import ExifTags
import multiprocessing

def build_preview_image(details):
	""" Generate a single preview image """
	
	filename = details['input_file']
	output_filename = details['output_file']
	
	# Define goal preview size
	preview_size = 2048, 2048
	
	# Open the existing image
	img = Image.open(filename)
	
	# Handle orientation
	for orientation in ExifTags.TAGS.keys():
		if ExifTags.TAGS[orientation]=='Orientation':
			break
	
	if hasattr(img, '_getexif'):
		this_exif = img._getexif()
		if this_exif is not None:
			exif = dict(this_exif.items())
			orientation = exif[orientation]
			
			if orientation == 3:
				img = img.transpose(Image.ROTATE_180)
			elif orientation == 6:
				img = img.transpose(Image.ROTATE_270)
			elif orientation == 8:
				img = img.transpose(Image.ROTATE_90)
	
	# Generate the new image
	img.thumbnail(preview_size, Image.ANTIALIAS)
	
	# Save the preview file
	img.save(output_filename, 'JPEG')

def generate_previews(path, num_workers=3):
	""" Generate previews for all jpgs in the given path """
	
	# Make sure the path has a trailing slash
	if path[-1] != '/':
		path = path + '/'

	# Attempt to create a previews directory
	try:
		os.mkdir(path + 'previews/')
	except OSError:
		pass
	
	# Get all filenames in the given dir
	dir_list = os.listdir(path)
	
	# Grab all jpgs from that list
	jpg_list = []
	for filename in dir_list:
		split_filename = filename.lower().split('.')
		if len(split_filename) > 1 and split_filename[1] == 'jpg':
			jpg_list.append(path + filename)
	
	jobs_list = []
	
	for filename in jpg_list:
		
		output_filename = filename.replace(path, path + 'previews/')
		
		jobs_list.append({
			'input_file' : filename,
			'output_file' : output_filename,
		})
	
	# Create separate worker to constantly monitor size of dir
	monitor_proc = multiprocessing.Process(target=monitor_output, args=(len(jpg_list), path + 'previews/'))
	monitor_proc.start()
	
	# Create and start worker pool
	worker_pool = multiprocessing.Pool(num_workers)
	worker_pool.map(build_preview_image, jobs_list)

def monitor_output(total_jobs, path):
	while True:
		num_previews = len(os.listdir(path))
		
		if num_previews == total_jobs:
			print('Complete')
			break
		
		percent_done = num_previews / (total_jobs + 1.0)
		percent_done = percent_done * 100
		percent_done = int(percent_done)
		
		output = str(num_previews) + '/' + str(total_jobs)
		output += ' (' + str(percent_done) + '%)'

		print(output)
		time.sleep(1)

if __name__ == '__main__':
	""" Takes a directory, and creates small versions of all found .jpg files """
	
	if len(sys.argv) > 1:
		generate_previews(sys.argv[1])
	else:
		print('Needs path to image dir')

