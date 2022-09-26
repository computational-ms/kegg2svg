import click
from .kegg2svg import convert

# @click.option("-l10", "--quant_log_10")


@click.command()
@click.argument("kegg_html", type=click.Path())
@click.argument("output_filename", type=click.Path())
@click.option(
    "-q",
    "--quant_file",
    "quant_file",
    default=None,
    type=click.Path(),
    help="Quant csv file. Columns must be `ID, value`, whereas ID can be any KEGG Metabolite or Reaction ID",
)
def cli(kegg_html, output_filename, quant_file=None):
    convert(kegg_html, output_filename, quant_file=quant_file)
