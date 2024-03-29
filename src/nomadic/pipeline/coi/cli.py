import click
from nomadic.pipeline.cli import cli
from .trim.commands import trim
from .panmap.commands import panmap
from .overlap.commands import overlap
from .align.commands import align
from .plot.commands import plot


@cli.group()
def coi():
    """
    COI estimation tools.

    """
    pass

coi.add_command(trim)
coi.add_command(panmap)
coi.add_command(overlap)
coi.add_command(align)
coi.add_command(plot)