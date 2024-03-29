import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def plot_dataframe_heat(
    df,
    title=None,
    cmap="bwr",
    cbar=None,
    as_log=False,
    label_values=True,
    output_path=None,
    **kwargs,
):
    """
    Create a `plt.imshow` like visualisation of a data frame

    """

    # Set figure size proportional to data frame
    r, c = df.shape
    rescale = 0.6
    fig, ax = plt.subplots(1, 1, figsize=(c * rescale, r * rescale))

    # Plot
    cax = ax.matshow(np.log(df) if as_log else df, cmap=cmap, **kwargs)

    # Colorbar
    if cbar is not None:
        fig.colorbar(
            cax,
            shrink=0.85 if c > 10 else 0.8,
            pad=0.01 if c > 10 else 0.05,
            label=cbar,
        )

    # Axis, Ticks, Grid
    ax.xaxis.set_label_position("top")
    ax.set_yticks(range(r))
    ax.set_xticks(range(c))
    ax.set_yticks(np.arange(0.5, r + 0.5), minor=True)
    ax.set_xticks(np.arange(0.5, c + 0.5), minor=True)
    ax.set_yticklabels(df.index)
    ax.set_xticklabels(df.columns, rotation=90)
    ax.grid(which="minor", ls="dotted")

    # Optional title
    if title is not None:
        ax.set_title(title)

    # Text labels
    if label_values:
        tau = np.quantile(a=df, q=0.2)
        for i in range(r):
            for j in range(c):
                v = df.iloc[i, j]
                if 0 <= v <= 1:
                    t = "%.02f" % v
                else:
                    t = "%.0f" % v
                if cmap in ["bwr"]:
                    ax.text(
                        j,
                        i,
                        t,
                        va="center",
                        ha="center",
                        size=7,
                        color="black" if v >= tau else "white",
                    )
                else:
                    ax.text(j, i, t, va="center", ha="center", size=7, color="black")

    # Optionally save figure
    if output_path is not None:
        fig.savefig(output_path, bbox_inches="tight", pad_inches=0.5, dpi=300)
        plt.close(fig)

    return None


class BalancePlotter:

    scale_size = 0.25
    
    NOMADS8_ORDER = [
        "CRT1",
        "DHFR",
        "DHPS",
        "K13",
        "MDR1",
        "MSP2",
        "PMI",
        "PMIII"
    ]
    NOMADS8_COLS = sns.color_palette("Spectral", 8)   
    
    NOMADS16_ORDER = NOMADS8_ORDER + [
        "AMA1",
        "CSP",
        "HRP2up",
        "HRP2",
        "HRP2dwn",
        "HRP3up",
        "HRP3",
        "HRP3dwn"
    ]
    NOMADS16_COLS = NOMADS8_COLS + sns.color_palette("inferno", 8)

    def __init__(self, sample_ids, gene_names, values, sample_id_order=None):
        """
        Plot a statistics `values` across `sample_ids` and `genes`

        """

        # Store instance variables
        self.sample_ids = sample_ids
        self.gene_names = gene_names
        self.values = values

        # Create data frame
        self.df = pd.DataFrame(
            {"sample_id": sample_ids, "gene_name": gene_names, "value": values}
        )

        # UNIQUE
        # sample_ids
        self.unique_sample_ids = np.unique(self.sample_ids)
        self.n_sample_ids = self.unique_sample_ids.shape[0]
        if sample_id_order is not None: # optionally set order of IDs
            assert all([s in self.unique_sample_ids for s in sample_id_order])
            self.unique_sample_ids = np.array(sample_id_order)
        # gene_names
        self.unique_gene_names = np.unique(self.gene_names)
        self.n_gene_names = self.unique_gene_names.shape[0]

        # Create sample_id axis map
        self._sample_axis_map()

    def _sample_axis_map(self):
        """
        Create a map from sample id to axis position

        """

        # Prepare ticks and limits
        self.sample_pos = np.arange(self.n_sample_ids)
        self.sample_pos_min = self.sample_pos.min()
        self.sample_pos_max = self.sample_pos.max()

        # Map
        self.id_to_pos = {
            sample_id: pos
            for sample_id, pos in zip(self.unique_sample_ids, self.sample_pos)
        }
        self.pos_to_id = {  # safer to reverse map, in case needed
            pos: sample_id for sample_id, pos in self.id_to_pos.items()
        }

    def get_sample_axis_pos(self, sample_id, jitter=True):
        """
        Return the axis position of a sample

        """

        y = self.id_to_pos[sample_id]
        if jitter:
            y += (random.random() - 0.5) * self.scale_size * 1.8

        return y

    def set_gene_color_pal(self, pal, nomads_panel=True):
        """
        Set color palette for the genes

        """
        # Generic approach
        self.gene_col = dict(
            zip(self.unique_gene_names, sns.color_palette(pal, self.n_gene_names))
        )
        
        # Hacky approach to quickly get colors for manuscript
        if nomads_panel and self.n_gene_names == 8:
            self.gene_col = dict(zip(self.NOMADS8_ORDER, self.NOMADS8_COLS))
        elif nomads_panel and self.n_gene_names == 16:
            self.gene_col = dict(zip(self.NOMADS16_ORDER, self.NOMADS16_COLS))

    def plot(self, show_imb_factor=True, output_path=None):
        """
        Create the balance plot

        """

        # Prepare canvas
        fig, ax = plt.subplots(figsize=(5, self.scale_size * self.n_sample_ids))

        # Plot
        for gene, gene_df in self.df.groupby("gene_name"):
            ax.scatter(
                y=gene_df["sample_id"].apply(self.get_sample_axis_pos),
                x=gene_df["value"],
                color=self.gene_col[gene],
                label=gene,
                ec="black",
                alpha=0.8,
            )

        # Scale
        ax.set_xscale("log")

        # Sample limits, ticks and labels
        ax.set_ylim(self.sample_pos_min - 1, self.sample_pos_max + 1)
        ax.set_yticks(self.sample_pos)
        ax.set_yticklabels(map(lambda p: self.pos_to_id[p], self.sample_pos))

        # Value label
        ax.set_xlabel("No. Reads\nOverlapping Target")

        # Invert yaxis
        ax.invert_yaxis()

        # Ticks
        ax.set_xlim(0, 5*10**4)
        ax.set_xticks([10**k for k in range(5)])
        ax.tick_params(axis='x', which='minor')
        ax.set_axisbelow(True)
        ax.grid(ls="dotted", axis="x", zorder=-10)
        ax.axvline(x=100, color="black", zorder=-10)

        # Optionally annotate with imbalance factors
        if show_imb_factor:
            imb_factors = {
                sample_id: sdf["value"].max()/(sdf["value"].min()+1)
                for sample_id, sdf in self.df.groupby("sample_id")
            }
            for sample_id, imb_factor in imb_factors.items():
                ax.annotate(
                    xy=(ax.get_xlim()[1], self.id_to_pos[sample_id]),
                    xycoords="data",
                    ha="left",
                    va="center",
                    color="black",
                    text=f" {imb_factor:.0f}x",
                )

        # Delineate barcodes
        improve_delin = True
        if improve_delin:
            for j in range(self.n_sample_ids)[::2]:
                ax.axhline(
                    j, lw=12, color="lightgrey", alpha=0.5, zorder=-10
                )

        # Legend
        ax.legend(loc="lower left", bbox_to_anchor=(0, 1), ncol=3)

        # Save
        if output_path is not None:
            fig.savefig(output_path, bbox_inches="tight", pad_inches=0.5, dpi=300)
            plt.close(fig)
