import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from nomadic.lib.references import (
    PlasmodiumFalciparum3D7,
    PlasmodiumFalciparumDd2,
    PlasmodiumFalciparumGB4,
    PlasmodiumFalciparumHB3,
)
from nomadic.lib.references import PF_REF_PALETTE
from nomadic.lib.parsing import build_parameter_dict
from nomadic.lib.generic import produce_dir, print_header, print_footer
from nomadic.pipeline.coi.trim.targets import TARGET_COLLECTION
from .main import load_paf


def plot_overview(expt_dir, config, target_gene):
    """
    Filter and trim all reads in a BAM file to overlap a `target_gene`
    and span `start` and `end` positions; then convert to FASTQ

    """

    # PARSE INPUTS
    script_descrip = "NOMADIC: Plot results of COI analysis"
    t0 = print_header(script_descrip)
    script_dir = "coi"
    params = build_parameter_dict(expt_dir, config, barcode=None)

    target = TARGET_COLLECTION[target_gene]
    print("User inputs:")
    print(f"  Target: {target.name}")
    print(f"  Chrom: {target.chrom}")
    print(f"  Start: {target.start}")
    print(f"  End: {target.end}")
    print("Done.\n")

    # References
    references = [
        PlasmodiumFalciparum3D7(),
        PlasmodiumFalciparumDd2(),
        PlasmodiumFalciparumGB4(),
        PlasmodiumFalciparumHB3(),
    ]

    # ITERATE
    print("Iterating over barcodes...")
    barcode_dfs = []
    for barcode in params["barcodes"]:
        print("." * 80)
        print(f"Barcode: {barcode}")
        print("." * 80)

        # DIRECTORIES
        # Inputs
        barcode_dir = f"{params['barcodes_dir']}/{barcode}"
        coi_dir = f"{barcode_dir}/coi"

        # Clipped read information
        fastq_csv_path = (
            f"{coi_dir}/fastq_clipped/reads.target.{target_gene}.clipped.csv"
        )
        try:
            read_df = pd.read_csv(fastq_csv_path)
        except pd.errors.EmptyDataError:  # Can happen with NTCs
            print(f"No FASTQ data found for {target_gene} and {barcode}.")
            continue

        # Load Panmap dataframes
        panmap_dfs = []
        for r in references:

            # Load
            input_paf = f"{coi_dir}/panmap/{barcode}.{r.name}.{target_gene}.sorted.paf"
            paf_df = load_paf(input_paf)
            paf_df.insert(0, "barcode", barcode)
            paf_df.insert(1, "reference", r.name)

            # Remove duplicate mappings, if they exist
            # retaining highest MAPQ
            if paf_df["query_name"].duplicated().any():
                paf_df.sort_values(
                    ["query_name", "mapq"], ascending=False, inplace=True
                )
                paf_df.drop_duplicates("query_name", inplace=True)

            # Store
            panmap_dfs.append(paf_df)

        # Combine
        panmap_df = pd.concat(panmap_dfs)

        # Merge in highest identity across panel mapping
        panmap_wide_df = pd.pivot(
            index="query_name", columns="reference", values="identity", data=panmap_df
        )
        highest_identity_ref = panmap_wide_df.idxmax(axis=1)
        highest_identity_ref.name = "highest_identity_ref"
        read_df = pd.merge(
            left=read_df,
            right=highest_identity_ref,
            left_on="read_id",
            right_index=True,
        )
        read_df.insert(0, "barcode", barcode)

        # Store
        barcode_dfs.append(read_df)

    # Concat and merge with metadata
    overview_df = pd.concat(barcode_dfs)
    overview_df = pd.merge(
        left=overview_df, right=params["metadata"], on="barcode", how="left"
    )
    overview_df["highest_identity_ref"] = pd.Categorical(
        values=overview_df["highest_identity_ref"],
        categories=[r.name for r in references],
        ordered=True)

    # Plot read lengths
    # TODO: wrap this
    size_scale = 0.25
    n_barcodes = len(params["barcodes"])
    fig, ax = plt.subplots(1, 1, figsize=(2, n_barcodes * size_scale))

    sns.stripplot(
        y="sample_id",
        x="length",
        hue="highest_identity_ref",
        palette=PF_REF_PALETTE,
        alpha=0.5,
        s=1,
        data=overview_df,
        ax=ax,
    )

    # Labels
    ax.set_title(target_gene, loc="left")
    ax.set_ylabel("")
    ax.set_xlabel("ORF Read Length (bp)")

    # Limits
    if target_gene == "CSP":
        ax.set_xlim((800, 1600))
    elif target_gene == "MSP2":
        ax.set_xlim((650, 1000))
        #ax.set_xlim((600, 1100))

    # Ticks and grid
    ax.set_axisbelow(True)
    start, end = ax.get_xlim()
    minorx, majorx = (50, 100) if (end - start) < 1200 else (50, 200)
    ax.xaxis.set_major_locator(plt.MultipleLocator(majorx))
    ax.xaxis.set_minor_locator(plt.MultipleLocator(minorx))
    ax.grid(ls="dotted", alpha=0.5)

    # Delineate barcodes
    improve_delin = True
    if improve_delin:
        for j in range(n_barcodes)[::2]:
            ax.axhline(j, lw=12, color="lightgrey", alpha=0.5, zorder=-10)

    # Legend
    ax.legend(
        title="Highest Similarity",
        bbox_to_anchor=(1, 1),
        loc="upper left",
        frameon=False,
    )
    output_dir = produce_dir(params["nomadic_dir"], "coi")
    fig.savefig(
        f"{output_dir}/plot.read_lengths.{target_gene}.pdf",
        dpi=300,
        pad_inches=0.5,
        bbox_inches="tight",
    )
    plt.close(fig)

    print_footer(t0)
