"""
"""
import pathlib
import urllib.parse
import urllib.request

from shapely import simplify
from shapely.geometry import shape
import pyglottography
from csvw.dsv import reader, UnicodeWriter
from clldutils.jsonlib import load, dump
from cldfgeojson.create import feature_collection, shapely_fixed_geometry

SOURCES = {
    10731: 'Glottolog',
    1: 'Asher & Moseley 2007',
    2: 'MML 2015',
    6: 'BFS 2005',
    3453: 'Asher & Moseley 2007',
    3451: 'TITUS',
    5617: 'Gamudze, Hadzata and King 2013',
}


class Dataset(pyglottography.Dataset):
    dir = pathlib.Path(__file__).parent
    id = "carling2025diacl"
    #_buffer = None

    def get(self, url, refresh=False):
        url = 'https://diacl.uni-frankfurt.de/' + url
        purl = urllib.parse.urlparse(url)
        path = self.raw_dir / purl.path.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        if refresh or (not path.exists()):
            if not refresh:
                print(path)
            try:
                urllib.request.urlretrieve(url, path)
            except:
                print('---', path)
                pass
        return path

    def cmd_download(self, args):
        srcss = {int(r['id']): r for r in self.raw_dir.read_csv('sources.csv', dicts=True)}
        geofeatures, mdfeatures = [], []
        for i, lg in enumerate(reader(self.get('Language/CSV/List', refresh=True), delimiter=';', dicts=True)):
            md = load(self.get('Language/JSON/' + lg['LanguageId'], refresh=True))#True))
            tfs = sorted({(gpmd['TimeFrame']['From'], gpmd['TimeFrame'].get('Until')) for gpmd in
                   md['GeographicalPresences'].values()}, reverse=True)
            if len(md['GeographicalPresences']) > 1:  # All presences pertain to the same timeframe.
                assert (len(tfs) == 1) or int(lg['LanguageId']) == 36500
            for gpid, gpmd in md['GeographicalPresences'].items():
                sources = set()
                year = tfs[0][0]
                if year == 175:
                    year = 1750
                if year != 1750:
                    assert tfs[0][0] <= 1750 <= (tfs[0][1] or 2000), lg['Name']
                    year = 1750
                for d in gpmd['SourceReferences']:
                    for sid in {d['FkSourceId']} if isinstance(d['FkSourceId'], int) else set(d['FkSourceId']):
                        assert sid in srcss
                    sources |= {d['FkSourceId']} if isinstance(d['FkSourceId'], int) else set(d['FkSourceId'])
                sources = [SOURCES[s] for s in sources]
                sources = '; '.join(sorted(sources))
                geojson_path = self.get('GeographicalPresence/GeoJSON/' + gpid)
                feature = load(geojson_path)
                if geojson_path.stat().st_size > 1000000:
                    feature['geometry'] = simplify(shape(feature['geometry']), tolerance=0.005).__geo_interface__
                #shapely_fixed_geometry(feature)
                del feature['crs']
                if 'bbox' in feature['geometry']:
                    del feature['geometry']['bbox']
                feature['properties'].update(
                    name=lg['Name'], year=year, id=gpid, map_name_full=sources)
                geofeatures.append(feature)
                mdfeatures.append(dict(
                    name=lg['Name'],
                    year=year,
                    id=gpid,
                    glottocode=lg['Glottocode'],
                    map_name_full=sources))

        #
        # FIXME: Add source metadata - or URL to DIACL website? https://diacl.uni-frankfurt.de/Source/Details/3451
        #
        dump(feature_collection(geofeatures), self.raw_dir / 'dataset.geojson')
        cols = ['id', 'name', 'glottocode', 'year', 'map_name_full']
        with UnicodeWriter('f.csv') as writer:
            writer.writerow(cols)
            for feature in sorted(mdfeatures, key=lambda f: int(f['id'])):
                writer.writerow([feature[col] for col in cols])
