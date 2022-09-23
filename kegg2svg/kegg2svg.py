import json
import csv
import re
from pathlib import Path
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


def parse_html(kegg_html):
    tree_data = []
    found_map_tag = False
    for line in open(kegg_html):
        if "<map id=" in line:
            found_map_tag = True
        if found_map_tag is True:
            tree_data.append(line.strip())
        if "</map>" in line:
            break
    return ET.fromstring("".join(tree_data))


def convert(kegg_html, output_filename):
    lookup = {}
    reaction_pattern = re.compile(r" (?P<reaction>R[0-9]{5})")

    color_file = Path(__file__).parent / "colors.csv"
    with open(color_file) as csv_reader:
        for _d in csv.DictReader(csv_reader):
            lookup[_d["ID"]] = _d

    root = parse_html(kegg_html)

    params = {
        "max_x": 0,
        "max_y": 0,
    }
    for g in root.findall("area[@shape='circle']"):
        x, y, r = g.attrib["data-coords"].split(",")
        params["max_x"] = max(params["max_x"], int(x))
        params["max_y"] = max(params["max_y"], int(y))
    logger.debug("Max map dimensions: {max_x} {max_y}".format(**params))
    d = draw.Drawing(
        params["max_x"] * 1.05,
        params["max_y"] * 1.05,
        origin=(0, 0),
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
                lookup.get(reactions[0], {"Color": "#cccccc"})["Color"] + "77"
            )
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
            lookup.get(
                cmpd,
                {"Color": "#cccccc"},
            )["Color"]
            + "77"
        )
        # logger.debug(f"Drawing {g.attrib['title']} at {x} {y}")
        element = draw.Circle(
            int(x), params["max_y"] - int(y), int(r) * 2, **circle_attributes
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
