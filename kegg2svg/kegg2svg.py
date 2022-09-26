import csv
import re
from pathlib import Path
from xml import dom
import xml.etree.ElementTree as ET
from loguru import logger
import drawSvg as draw


class Hyperlink(draw.DrawingParentElement):
    TAG_NAME = "a"

    def __init__(self, href, target=None, **kwargs):
        # Other init logic...
        # Keyword arguments to super().__init__() correspond to SVG node
        # arguments: stroke_width=5 -> stroke-width="5"
        super().__init__(href=href, target=target, **kwargs)


class D3Scale:
    def __init__(self, domain, range):
        """Python implementation of d3 scales.

        Maps values from a domain onto a range. Currently only linear is supported.

        Args:
            domain (tuple): min, max values for domain
            range (tuple): min, max values for range
        """
        self.domain = domain
        self.range = range
        self.delta_domain = domain[1] - domain[0]
        self.delta_range = range[1] - range[0]
        if self.delta_domain == 0:
            logger.warning("Domain range must be bigger than 0!")
            raise ZeroDivisionError

        if self.delta_range == 0:
            logger.warning("Range range must be bigger than 0!")
            raise ZeroDivisionError

    def map(self, value):
        """Map value onto range.

        Args:
            value (float):
        """
        value = max(min(self.domain), value)
        value = min(max(self.domain), value)
        domain_fraction = (value - min(self.domain)) / self.delta_domain
        if domain_fraction < 0:
            domain_fraction += 1

        mapped_value = self.range[0] + self.delta_range * domain_fraction
        return mapped_value


def parse_html(kegg_html):
    """Parse KEGG map.HTML.

    Args:
        kegg_html (html): use `curl -O <your_mal_link> map0.htlm` to get the html

    Returns:
        ElementTree: Matabolite and Path elements from HTML page
    """
    tree_data = []
    found_map_tag = False
    for line in open(kegg_html, "r"):
        if "<map id=" in line:
            found_map_tag = True
        if found_map_tag is True:
            tree_data.append(line.strip())
        if "</map>" in line:
            break
    return ET.fromstring("".join(tree_data))


def read_csv(f):
    """Read csv file using DictReader

    Args:
        f (csv): Csv file

    Yields:
        dict: For each row in the csv
    """
    with open(f, "r") as csv_reader:
        for _d in csv.DictReader(csv_reader):
            yield _d


def parse_quant_file(quant_file):
    """Parse Quantfile that shall be mapped ont the KEGG Map

    Args:
        quant_file (csv): Requires columns ID and value

    Returns:
        dict: key KEGG ID Rxxxxx or Cxxxxx as key and quant value as value
    """
    qlookup = {}
    for _d in read_csv(quant_file):
        qlookup[_d["ID"]] = float(_d["value"])
    return qlookup


def parse_color_file():
    """Parse color file.

    Returns:
        dict: key KEGG ID Rxxxxx or Cxxxxx as key and color as value
    """
    clookup = {}
    color_file = Path(__file__).parent / "colors.csv"
    for _d in read_csv(color_file):
        clookup[_d["ID"]] = _d
    return clookup


def convert(
    kegg_html,
    output_filename,
    quant_file=None,
    min_radius_multiplier=2,
    max_radius_multiplier=10,
    min_stroke_multiplier=0.2,
    max_stroke_multiplier=10,
):
    """Convert Kegg HTML to CSV.

    Args:
        kegg_html (html): KEGG html page. Use e.g. `curl -O https://www.genome.jp/pathway/map01100 map01100.html`
        output_filename (str):
        quant_file (csv, optional): Requires ID and value as columns. Defaults to None.
        min_radius_multiplier (int, optional): Minimum radius multiplier for metabolites. Defaults to 2.
        max_radius_multiplier (int, optional): Maximum radius multiplier for metabolites. Defaults to 10.
        v--- reaction path scaling not implemented yet
        min_stroke_multiplier (int, optional): Minimum stroke mulitplier for reactions. Defaults to 0.2.
        max_stroke_multiplier (int, optional): Maximum stroke mulitplier for reactions. Defaults to 4.
    """
    params = {
        "max_x": 0,
        "max_y": 0,
        "min_quant": 0,
        "max_quant": 1,
        "max_r": 0,
    }
    reaction_pattern = re.compile(r" (?P<reaction>R[0-9]{5})")
    quant_lookup = {}
    if quant_file is not None:
        quant_lookup = parse_quant_file(quant_file)
        params["max_quant"] = max(list(quant_lookup.values()))
        params["min_quant"] = min(list(quant_lookup.values()))
        logger.debug("Quant value range: {min_quant} {max_quant}".format(**params))

    color_lookup = parse_color_file()

    root = parse_html(kegg_html)

    for g in root.findall("area[@shape='circle']"):
        x, y, r = g.attrib["data-coords"].split(",")
        params["max_x"] = max(params["max_x"], int(x))
        params["max_y"] = max(params["max_y"], int(y))
        params["max_r"] = max(params["max_r"], int(r))
    logger.debug("Max map dimensions: {max_x} {max_y}".format(**params))

    qscale = D3Scale(
        domain=(
            params["min_quant"],
            params["max_quant"],
        ),
        range=(
            params["max_r"] * min_radius_multiplier,
            params["max_r"] * max_radius_multiplier,
        ),
    )

    d = draw.Drawing(
        params["max_x"] * 1.05,
        params["max_y"] * 1.05,
        origin=(0, -0.025 * params["max_y"]),
        displayInline=False,
    )

    for g in root.findall("area[@shape='poly']"):
        coords = []
        for pos, c in enumerate(g.attrib["data-coords"].split(",")):
            if pos % 2 == 0:  # x-coords
                coords.append(int(c))
            else:
                coords.append(params["max_y"] - int(c))
        reactions = reaction_pattern.findall(g.attrib["title"])
        line_attributes = {
            "fill": "#44444477",
            "stroke": None,
            "stroke_width": 0.2,
        }
        if len(reactions) == 1:
            line_attributes["fill"] = (
                color_lookup.get(reactions[0], {"Color": "#cccccc"})["Color"] + "77"
            )
            quant_value = quant_lookup.get(reactions[0], None)
            if quant_value is not None:
                logger.debug("Reaction path scaling not implemented yet.")
        element = draw.Lines(*coords, **line_attributes)
        element.appendTitle(f"{g.attrib['title']}")
        hlink = Hyperlink(f"https://www.genome.jp{g.attrib['href']}", target="_blank")
        hlink.append(element)
        d.append(hlink)

    for g in root.findall("area[@shape='circle']"):
        x, y, r = g.attrib["data-coords"].split(",")
        circle_attributes = {
            # "fill": "#44444477",
            "stroke": None,
            # "stroke_width": 0.2,
        }
        cmpd = g.attrib["href"].split("/")[-1]
        circle_attributes["fill"] = (
            color_lookup.get(
                cmpd,
                {"Color": "#cccccc"},
            )["Color"]
            + "77"
        )
        quant_value = quant_lookup.get(cmpd, None)
        if quant_value is None:
            radius = int(r) * min_radius_multiplier
        else:
            radius = qscale.map(int(quant_value))

        element = draw.Circle(
            int(x),
            params["max_y"] - int(y),
            radius,
            **circle_attributes,
        )
        element.appendTitle(f"{g.attrib['title']}")
        hlink = Hyperlink(f"https://www.genome.jp{g.attrib['href']}", target="_blank")
        hlink.append(element)
        d.append(hlink)

    ratio = params["max_y"] / params["max_x"]
    d.setRenderSize(
        1200,
        1200 * ratio,
    )
    if output_filename.endswith(".svg") is False:
        output_filename += ".svg"
    d.saveSvg(output_filename)
    logger.debug(f"Wrote {output_filename}")
