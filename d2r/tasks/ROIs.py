import os
import pathlib
from osgeo import gdal
import numpy as np
from PIL import Image
from tqdm import tqdm

from d2r.task import Task
import d2r.misc

class ROIs(Task):
	def run(self, dataset):
		#making sure the output subfolder do exists
		path = pathlib.Path(self.config['outfolder'], dataset.get_title())
		path.mkdir(parents=True, exist_ok=True)
		
		#the geometry index, whose values are also used for filenames
		geoid = dataset.get_geom_index()
		
		#for each ROI
		for i in tqdm(dataset.get_geom_field(geoid)):
			#build the outfile name, without the extension
			outfile = os.path.join(path, 'ROI_' + str(i))
			
			#saving each requested format
			if self.config['tif'] : self._save_tif(outfile, dataset, geoid, i)
			if self.config['png'] : self._save_png(outfile, dataset, geoid, i)

	def _save_tif(self, outfile, dataset, geoid, current):
			#build the outfile name
			outfile_current = outfile + '.tif'
			
			#check if we should do this ROI or not
			if os.path.isfile(outfile_current) and self.config['skip_if_already_done']:
				print('skipping, output file already exists: ' + outfile_current)
				return(None)
			
			#extract the data
			rb = dataset.get_geom_raster(polygon_id=current, polygon_field=geoid)
			
			if rb is None:
				print('Empty ROI, field=' + str(geoid) + ' value=' + str(current))
				next
			
			#save the data
			rows, cols, bands = rb.shape
			
			#new raster dataset (TIFF format)
			driver = gdal.GetDriverByName('GTiff')
			outdataset = driver.Create(outfile_current, cols, rows, bands, gdal.GDT_Float32)

			#should we add georeferences/projection too?
			
			#write each channel
			for ch in range(bands):
				band = outdataset.GetRasterBand(ch + 1)
				band.WriteArray(rb[:,:,ch])
				#band.SetNoDataValue(outdataset.get_nodata_value())
				band.FlushCache()
			
			#closing and saving
			outdataset = None
		
	def _save_png(self, outfile, dataset, geoid, current):
			#build the outfile name
			outfile_current = outfile + '.png'
			
			#check if we should do this ROI or not
			if os.path.isfile(outfile_current) and self.config['skip_if_already_done']:
				print('skipping, output file already exists: ' + outfile_current)
				return(None)
			
			#extract the data
			rb = dataset.get_geom_raster(polygon_id=current, polygon_field=geoid, normalize_if_possible=True)
			
			if rb is None:
				print('Empty ROI, field=' + str(geoid) + ' value=' + str(current))
				next
			
			#what are the visible channels, out of the available ones?
			channels = dataset.get_channels()
			visible_channels = dataset.get_visible_channels()
			selected = [channels.index(i) for i in visible_channels]
			
			#extracting the target data
			rb_visible = rb[:,:,selected]
			
			#should we stretch the data to 0-255?
			if self.config['png_stretch_to_0-255']:
				mymin = np.min(rb_visible)
				mymax = np.max(rb_visible)
				rb_visible = 255.0 * (rb_visible - mymin) / (mymax - mymin)

			#saving
			Image.fromarray(rb_visible.astype(np.uint8)).save(outfile_current)
		
	def parse_config(self, config):
		"""parsing config parameters specific to this subclass"""
		res = super().parse_config(config)

		for key in res:
			if key in ['tif', 'png', 'png_stretch_to_0-255']:
				res[key] = d2r.misc.parse_boolean(res[key])

		return(res)