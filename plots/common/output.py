import os,shutil


import logging
logger = logging.getLogger("OutputFolder")

try:
    from shortuuid import uuid
except:
    logger.error("Couldn't open shortuuid. Please install using setup/install_pylibs.sh")
    def uuid():
        return "FIXME_UUID"

class OutputFolder:
    """
    This class summarizes gathering output in a sytematic way. It is repsonsible for creating and deleting
    the output folder when necessary, and can create subdirectories with unique names.
    """


    def __init__(self, out_folder=None, **kwargs):
        """
        out_folder - the path to the output folder (need not exist).
            This is the base of the output, to which a unique name may be added

        optional arguments:
        overwrite - (bool) do you want to delete the output folder if it exists=
        unique_subdir - (bool) do you want to create a UUID for the output folder,
            to separate output from the previous run of the calling script?
        subdir - a path in out_folder_UNIQUEID/subdir which will be used for output.
            Useful if you have multiple logically
            separate things going to the same output folder.
        """
        if not out_folder:
            out_folder = os.path.join(os.environ["STPOL_DIR"], "out")
        self.out_folder = out_folder

        overwrite = kwargs.get("overwrite", False)
        subdir = kwargs.get("subdir", "")
        unique_subdir = kwargs.get("unique_subdir", False)
        if unique_subdir:
            self.out_folder += "_" + uuid()
        self.out_folder = os.path.join(self.out_folder, subdir)

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
        logger.debug("OutputFolder with %s" % self.out_folder)

    def get(self, path):
        """
        Returns a path in this folder, creating it if it doesn't exist.
        """
        _path = os.path.join(self.out_folder, path)
        try:
            os.makedirs(_path)
        except Exception as e:
            if not os.path.exists(_path):
                raise e
        return _path

    def savePlot(self, canvas, plot_meta, printOut=True):
        """
        Saves a ROOT.TCanvas into the folder and sets the metadata.
        canvas - an ROOT TCanvas
        plot_meta - a plots.common.metainfo.PlotMetaInfo object with the metadata for this canvas
        """
        subd = os.path.join(self.out_folder, plot_meta.subdir)
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

            if printOut:
                print "Saving plot to %s" % outpath
            #Can fail to export to PNG when libASImage is not available
            try:
                canvas.SaveAs(outpath)
                plot_meta.update(outpath)
            except e:
                logger.error("Couldn't save image: " + str(e))




