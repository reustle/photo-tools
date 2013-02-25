import os
import sys
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
	
	# Create and start worker pool
	worker_pool = multiprocessing.Pool(num_workers)
	worker_pool.map(build_preview_image, jobs_list)
		
if __name__ == '__main__':
	""" Takes a directory, and creates small versions of all found .jpg files """
	
	if len(sys.argv) > 1:
		generate_previews(sys.argv[1])
	else:
		print('Needs path to image dir')

