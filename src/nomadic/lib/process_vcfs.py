import os
import uuid
import shutil
import subprocess


def bcftools_view(input_vcf, output_vcf, dry_run=False, **kwargs):
    """
    Run `bcftools view` on an `input_vcf`

    params:
        input_vcf: str
            Path to input `.vcf`.
        output_vcf: str
            Path to output `.vcf`.
        dry_run: bool
            Print command instead of running it.
        kwargs: key=value
            Additional arguments will be passed to
            bcftools view as flags; e.g.
            `-<key> <value>`.

    returns
        None

    """

    cmd = f"bcftools view -I {input_vcf} "
    cmd += " ".join([f"-{k} {v}" for k, v in kwargs.items()])
    cmd += f" -o {output_vcf}"

    if dry_run:
        print(cmd)
        return

    subprocess.run(cmd, shell=True, check=True)


def bcftools_sort(input_vcf, output_vcf, dry_run=False, **kwargs):
    """
    Run `bcftools sort` on an `input_vcf`

    params:
        input_vcf: str
            Path to input `.vcf`.
        output_vcf: strbcft
            Path to output `.vcf`.
        dry_run: bool
            Print command instead of running it.
        kwargs: key=value
            Additional arguments will be passed to
            bcftools view as flags; e.g.
            `-<key> <value>`.

    returns
        None

    """

    cmd = f"bcftools sort {input_vcf} "
    cmd += " ".join([f"-{k} {v}" for k, v in kwargs.items()])
    cmd += f" -o {output_vcf}"

    if dry_run:
        print(cmd)
        return

    subprocess.run(cmd, shell=True, check=True)


def bcftools_index(input_vcf):
    """
    Run `bcftools index`

    params
        input_vcf : str
            VCF file to be indexed.

    returns
        None

    """

    cmd = f"bcftools index -f {input_vcf}"
    subprocess.run(cmd, shell=True, check=True)


def bcftools_reheader(input_vcf, output_vcf, sample_names):
    """
    Run `bcftools reheader` to change VCF sample name

    params
        input_vcf : str
            Input VCF.
        output_vcf : str
            Output VCF.
        sample_names : list of str
            Name of samples, in a list.

    returns
        None

    """

    # Generate random file name
    sample_file = f"sample_{str(uuid.uuid4())}.txt"

    # Write sample names to file
    with open(sample_file, "w") as fn:
        for sample_name in sample_names:
            fn.write(f"{sample_name}\n")

    # Create temporary file if input and output have same name
    if input_vcf == output_vcf:
        output_vcf = f"{input_vcf}".replace(".vcf", f"{str(uuid.uuid4())}.vcf")
        cleanup = True

    # Construct and run command
    cmd = "bcftools reheader"
    cmd += f" {input_vcf}"
    cmd += f" -s {sample_file}"
    cmd += f" -o {output_vcf}"

    subprocess.run(cmd, shell=True, check=True)

    # Remove file
    os.remove(sample_file)

    # Clean up, if necessary
    if cleanup:
        shutil.move(output_vcf, input_vcf)


def bcftools_merge(input_vcfs, output_vcf, dry_run=False, **kwargs):
    """
    Run `bcftools merge`

    params
        input_vcfs: list[str]
            List of paths to `.vcf` files that will be merged.
            Note that these need to be compressed for merge
            to work.
        output_vcf: str
            Path to output vcf.
        dry_run: bool
            Print command instead of running.

    """
    cmd = "bcftools merge"
    cmd += f" {' '.join(input_vcfs)} "
    cmd += " ".join([f"-{k} {v}" for k, v in kwargs.items()])
    cmd += f" -o {output_vcf}"

    if dry_run:
        print(cmd)
        return

    subprocess.run(cmd, shell=True, check=True)


def bcftools_concat(input_vcfs, output_vcf, dry_run=False, **kwargs):
    """
    Run `bcftools concat`

    """
    cmd = "bcftools concat"
    cmd += f" {' '.join(input_vcfs)} "
    cmd += " ".join([f"-{k} {v}" for k, v in kwargs.items()])
    cmd += f" -o {output_vcf}"

    if dry_run:
        print(cmd)
        return

    subprocess.run(cmd, shell=True, check=True)


def bcftools_query_samples(input_vcf, dry_run=False, **kwargs):
    """
    Run `bcftools query` to extract sample names from an input VCF

    """
    cmd = "bcftools query -l"
    cmd += f" {input_vcf} "
    cmd += " ".join([f"-{k} {v}" for k, v in kwargs.items()])

    if dry_run:
        print(cmd)
        return

    output = subprocess.check_output(cmd, shell=True)
    samples = output.decode().strip().split("\n")

    return samples
