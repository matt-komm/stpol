from libxmp import *
import os
from subprocess import check_call
from tempfile import NamedTemporaryFile, TemporaryFile
import glob

import logging
logger = logging.getLogger("metainfo.py")

class PlotMetaInfo:
	"""
	This class gathers the metadata information corresponding to a plot,
	and manages appending it to the output file of the plot using exiftools.
	Note that the metadata must be configured in the config file exif_cfg
	"""
	exif_cfg = os.path.join(os.environ["STPOL_DIR"], "plots/exif.config")

	@staticmethod
	def update_tags(xmp, fi):
		"""
		Appends the given XMP metadata to the file using a syscall to exiftools.
		xmp - an XMPMeta object with the required metadata
		fi - the path to the file that you want to append to
		"""
		logger.info("Updating tags for file %s" % fi)
		outs = xmp.serialize_to_str()
		with NamedTemporaryFile() as of:
			of.write(outs)
			of.flush()
			cmd = ["exiftool", "-config " + PlotMetaInfo.exif_cfg, "-tagsFromFile " + of.name, fi]
			logger.debug(" ".join(cmd))
			check_call(" ".join(cmd), shell=True, stdout=TemporaryFile())
		os.remove(fi+"_original")

	def __init__(self, title, cut, weight, infiles, subpath, comments=""):
		"""
		title - the title of the plot
		cut - the Cut object used to draw the plot
		weight - the weight object (or anything convertible to str) used to draw this plot
		infiles - a list with the paths to the input files used for this plot. symlinks will be expanded
		"""
		self.title = title
		self.cut = cut
		self.infiles = map(os.path.realpath, infiles)
		self.subpath = subpath
		self.weight = weight
		self.comments = comments

	def update(self, fn):
		"""
		Updates the tags in a given file. Anything done here must be reflected in the config file
		exif_cfg.
		fn - a path to the file to update
		"""
		xmp = XMPMeta()
		ns = xmp.register_namespace("XMP-stpol", "XMP-stpol")
		xmp.set_property("XMP-stpol", "infiles", " ".join(self.infiles))
		xmp.set_property("XMP-stpol", "title", str(self.title))
		xmp.set_property("XMP-stpol", "cut", str(self.cut))
		xmp.set_property("XMP-stpol", "weight", str(self.weight))
		xmp.set_property("XMP-stpol", "comments", str(self.comments))
		self.update_tags(xmp, fn)

if __name__=="__main__":
	fn = "/Users/joosep/Documents/data.xmp"
	logging.basicConfig(level=logging.INFO)

	# Read file
	xmp = XMPMeta()
	ns = xmp.register_namespace("XMP-stpol", "XMP-stpol")
	xmp.set_property("XMP-stpol", "infile", "blabla")

	meta = PlotMetaInfo("2j1t", "a a f")
	meta.update("/Users/joosep/Documents/stpol/out/plots/6/figures/control/3j1t_topMass_mu.pdf")

