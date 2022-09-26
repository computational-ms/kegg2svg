# kegg2svg

Simple Python package to convert KEGG HTML files to svg with the option to overlay quantitative data.

## Installation

`
pip install kegg2svg
`

Use virtualenv, if you can! :)

If you start of the git repo, you can use

`
python setup.py .
`


## Usage:

You will need the html from KEGG. You can get it e.g. via

`
curl "https://www.genome.jp/pathway/map01100" -o map01100.html
`

*NOTE* You MUST make sure to comply with the conditions of using KEGG http://www.kegg.jp/kegg/legal.html

Then you can convert the html to svg using:

`
kegg2svg map01100.html map01100.svg
`

### Adding quant data

`
kegg2svg map01100.html map01100.svg -q example_data/metabolite_quants_example.csv
`

Please refer to the example_data files for the format. Only _ID_ and _value_ columns are required. Scaling of reaction paths is not implemented yet.
