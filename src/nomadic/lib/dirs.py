import os

def produce_dir(*args):
    """
    Produce a new directory by concatenating `args`,
    if it does not already exist
    
    params
        *args: str1, str2, str3 ...
            Comma-separated strings which will 
            be combined to produce the directory,
            e.g. str1/str2/str3
    
    returns
        dir_name: str
            Directory name created from *args.
    
    """
    
    # Define directory path
    dir_name = os.path.join(*args)
    
    # Create if doesn't exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    return dir_name


class ExperimentDirectories:
    """

    """

    #ROOT_DIR = Path(__file__).absolute().parent.parent.parent
    #experiments_dir = produce_dir(ROOT_DIR, "experiments")
    experiments_dir = "experiments"

    def __init__(
        self,
        expt_name: str
    ):
        """
        Initialise all the required directories

        """
        # Experiment directory
        self.expt_name = expt_name
        self.expt_dir = produce_dir(self.experiments_dir, expt_name)

        # Metadata directory
        self.metadata_dir = produce_dir(self.expt_dir, "metadata")
        
        # MinKNOW directory
        self.minknow_dir = produce_dir(self.expt_dir, "minknow")

        # Directory
        self.dorado_dir = produce_dir(self.expt_dir, "dorado")
        
        # Nomadic dir
        self.nomadic_dir = produce_dir(self.expt_dir, "nomadic", "dorado", "sup", "single_end_strict")
        
        # Barcodes dir
        self.barcodes_dir = produce_dir(self.nomadic_dir, "barcodes")
        
    def get_barcode_dir(self, barcode: str) -> str:
        return produce_dir(self.barcodes_dir, barcode)