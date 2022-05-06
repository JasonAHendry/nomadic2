import os
from nomadic.lib.process_gffs import load_gff, add_gff_fields
from nomadic.lib.process_bams import samtools_mpileup
from .bed import TargetBEDBuilder


class ErrorAnalysisAlgorithm:
    def __init__(self, reference, output_dir):
        """
        Will define pipeline and hold intermediate file paths, data structures
        - Will need to also feed in information about strandedness of target
        
        """
        self.reference = reference
        self.output_dir = output_dir

    def load_gff(self): # Needed here?
        self.gff_df = load_gff(self.reference.gff_path)
        self.gff_df = add_gff_fields(self.gff_df, ["ID", "Name", "Parent"])

    def set_target(self, target_id):
        """ 
        Set the Target based on it's ID
        May want to include strand
        """
        self.target_id = target_id

    def create_target_bed(self, bed_builder: TargetBEDBuilder):
        """Create .bed file for the target"""

        # Define path
        self.bed_path = f"{self.output_dir}/{self.target_id}.bed" # might need approach

        # Write the BED
        bed_builder.set_target(self.target_id)
        bed_builder.find_bed_rows()
        bed_builder.write_bed(bed_path=self.bed_path)
        
    def create_target_mpileup(self, bam_path):
        """
        Create a target mpileup

        ISSUE: you could theoretically give a different .bam than you set the
        target id, these aren't linked by the software, must be done well
        by user
        Could produce a little check for this, maybe
        
        """
        # Make sure the BED file has been generated
        if self.bed_path is None:
            raise ValueError("No BED file is defined.")

        if not os.path.isfile(bam_path):
            raise FileNotFoundError(f"No .bam file found at {bam_path}. Check path.")
        self.bam_path = bam_path
        self.pileup_path = f"{self.output_dir}/{self.target_id}.mpileup"

        # Run samtools mpileup
        samtools_mpileup(
            input_bam=self.bam_path,
            ref_fasta=self.reference.fasta_path,
            target_bed=self.bed_path,
            output_pileup=self.pileup_path
        )

    def summarise_mpileup(self): # this is amino acid or nucleotide level
        pass