# Releasing the dataset

## Recreate the raw data from DiACL

```shell
cldfbench download cldfbench_carling2025diacl.py
```


## Recreate the CLDF data

```shell
cldfbench makecldf cldfbench_carling2025diacl.py --glottolog-version v5.2
cldfbench cldfreadme cldfbench_carling2025diacl.py
cldfbench zenodo --communities glottography cldfbench_carling2025diacl.py
cldfbench readme cldfbench_carling2025diacl.py
```

## Validation

Make sure the CLDF dataset is valid:

```shell
cldf validate cldf
```

Make sure the GeoJSON data contains only valid (Multi)Polygon shapes:

```shell
cldfbench geojson.validate cldf
```

The agreement with the point locations for languages given in Glottolog can be checked as follows.
Note that this requires the [csvkit](https://csvkit.readthedocs.io/en/latest/index.html) and
[termgraph](https://github.com/mkaz/termgraph) commands to be installed and the 
[Glottolog data repository](https://github.com/glottolog/glottolog) to be available locally.

We 
- compute the distances between polygon features in the language-level GeoJSON and the corresponding
  Glottolog location using the `cldfbench geojson.glottolog_distance` command, outputting the results
  as TSV, then
- reformat as CSV
- select only rows with distances greater than 2 grid units in the lat/lon coordinate system 
  (corresponding to about 220km close to the equator)
- join data about [outliers with known explanations](etc/known_outliers.csv) and
- filter these out
- sort by Distance and format the result suitable as input for `termgraph`
- pipe the data into `termgraph`

```shell
cldfbench geojson.glottolog_distance cldf --glottolog ../../glottolog/glottolog --glottolog-version v5.2 --format tsv | \
csvformat -t | \
csvgrep -c Distance -r"^[01]\.?" -i | \
csvjoin --left -c ID,Glottocode - etc/known_outliers.csv | \
csvgrep -i -c Comment -r".+" | \
csvsort -c Distance | \
csvcut -c ID,Distance | \
csvformat -E | \
termgraph
```

```
mara1408: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.14 
lizu1234: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.16 
west2386: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.16 
suii1243: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.27 
cree1270: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.36 
chey1247: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.38 
miam1252: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.48 
cint1239: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.62 
djeo1235: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.73 
cash1254: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 2.80 
arai1239: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.00 
yano1262: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.21 
plai1258: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.24 
sant1432: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.27 
pota1247: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.65 
pula1262: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.67 
nana1257: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.84 
mesk1242: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 3.97 
shee1238: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 4.58 
```

To get a better idea of the languages and distances, we can render the areas and Glottolog locations
as [GeoJSON file](etc/outliers.geojson) using the command below. This file can be inspected e.g. 
using the https://geojson.io/ service.

```shell
cldfbench geojson.glottolog_distance cldf --glottolog ../../glottolog/glottolog --glottolog-version v5.2 --format tsv | \
csvformat -t | csvgrep -c Distance -r"^[01]\.?" -i | \
csvjoin --left -c ID,Glottocode - etc/known_outliers.csv | csvgrep -i -c Comment -r".+" | \
csvcut -c ID | cldfbench geojson.geojson cldf - > etc/outliers.geojson
```

This inspection reveals that the majority of the outliers correspond to North American languages where
Glottolog locations often reflect today's reservations or poorly attested South American languages
where not much is known at all.
