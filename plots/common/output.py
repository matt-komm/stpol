import os,shutil

import shortuuid
import logging
logger = logging.getLogger("OutputFolder")

class OutputFolder:
	"""
	This class summarizes gathering output in a sytematic way. It is repsonsible for creating and deleting 
	the output folder when necessary, and can create subdirectories with unique names.
	"""


	def __init__(self, out_folder, **kwargs):
		"""
		out_folder - the path to the output folder (need not exist).
			This is the base of the output, to which a unique name may be added

		optional arguments:
		overwrite - (bool) do you want to delete the output folder if it exists=
		unique_subdir - (bool) do you want to create a UUID for the output folder,
			to separate output from the previous run of the calling script?
		subpath - a path in out_folder_UNIQUEID/subpath which will be used for output.
			Useful if you have multiple logically
			separate things going to the same output folder.
		"""
		self.out_folder = out_folder 

		overwrite = kwargs.get("overwrite", False)
		subpath = kwargs.get("subpath", "")
		unique_subdir = kwargs.get("unique_subdir", True)
		if unique_subdir:
			self.out_folder += "_" + shortuuid.uuid()
		self.out_folder = os.path.join(self.out_folder, subpath)

		if overwrite:
			logger.info("Deleting output folder %s" % self.out_folder)
			try:
				shutil.rmtree(self.out_folder)
			except:
				pass
		try:
			os.makedirs(self.out_folder)
		except Exception as e:
			if not os.path.exists(self.out_folder):
				raise e
		logger.info("OutputFolder with %s" % self.out_folder)

	def savePlot(self, canvas, plot_meta):
		"""
		Saves a ROOT.TCanvas into the folder and sets the metadata.
		canvas - an ROOT TCanvas
		plot_meta - a plots.common.metainfo.PlotMetaInfo object with the metadata for this canvas
		"""
		subd = os.path.join(self.out_folder, plot_meta.subpath)
		try:
			os.makedirs(subd)
			logger.info("Made subdirectory %s" % subd)
		except:
			pass
		logger.info("Plot subdirectory is " + subd)
		
		fname = plot_meta.title

		for format in ["pdf", "png"]:
			outpath = os.path.join(subd, fname + "." + format)
			logger.info("Saving plot to %s" % outpath)
			canvas.SaveAs(outpath)
			plot_meta.update(outpath)





