import click
from .kegg2svg import convert


@click.command()
@click.argument("kegg_html", type=click.Path())
@click.argument("output_filename", type=click.Path())
def cli(kegg_html, output_filename):
    convert(kegg_html, output_filename)
