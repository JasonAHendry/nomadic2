import click
import subprocess

from nomadic.lib.generic import print_header, print_footer
from nomadic.lib.parsing import build_parameter_dict
from nomadic.lib.process_bams import samtools_index
from nomadic.lib.references import (
    PlasmodiumFalciparum3D7,
    HomoSapiens,
)
from nomadic.pipeline.cli import experiment_options, barcode_option
from nomadic.pipeline.map.mappers import MAPPER_COLLECTION


# ================================================================
# Main script, run from `cli.py`
#
# ================================================================


@click.command(short_help="Map unmapped reads to H.s.")
@experiment_options
@barcode_option
@click.option(
    "-a",
    "--algorithm",
    type=click.Choice(MAPPER_COLLECTION),
    default="minimap2",
    help="Algorithm used to map reads."
)
def remap(expt_dir, config, barcode, algorithm):
    """
    Remap all reads that failed to map to P.f. referece genome
    to human referece genome

    """

    # PARSE INPUTS
    script_descrip = "NOMADIC: Re-map unmapped reads to Homo Sapiens"
    t0 = print_header(script_descrip)
    script_dir = "bams"
    params = build_parameter_dict(expt_dir, config, barcode)

    # Focus on a single barcode, if specified
    if "focus_barcode" in params:
        params["barcodes"] = [params["focus_barcode"]]

    # Define reference genomes
    pf_reference = PlasmodiumFalciparum3D7()
    hs_reference = HomoSapiens()

    # ITERATE
    print("Iterating over barcodes...")
    for barcode in params["barcodes"]:
        print("." * 80)
        print(f"Barcode: {barcode}")
        print("." * 80)

        # Define input and output bams
        barcode_dir = f"{params['barcodes_dir']}/{barcode}/{script_dir}"
        input_bam = f"{barcode_dir}/{barcode}.{pf_reference.name}.final.sorted.bam"
        output_bam = f"{barcode_dir}/{barcode}.{hs_reference.name}.final.sorted.bam"

        # Instantiate mapper
        mapper = MAPPER_COLLECTION[algorithm](hs_reference)

        # Remap
        print("Remapping to H.s...")
        mapper.remap_from_bam(input_bam)
        mapper.run(output_bam)

        # Index
        print("Indexing...")
        samtools_index(input_bam=output_bam)
        print("Done.")
        print("")
    print_footer(t0)
