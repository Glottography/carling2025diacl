"""
"""
import typing
import pathlib
import collections
import urllib.parse
import urllib.request

from pyglottography.dataset import Feature, FeatureSpec
from shapely import simplify
from shapely.geometry import shape
import pyglottography
from csvw.dsv import reader, UnicodeWriter
from clldutils.jsonlib import load, dump
from cldfgeojson.create import feature_collection, shapely_fixed_geometry

SOURCES = {
    10731: None,  # Only point coordinates are taken from Glottolog
    1: 'asher_moseley_2007',
    2: 'mml2015',
    6: 'bfs2005',
    3453: 'asher_moseley_2007',
    3451: 'titus',
    5617: None,  # Wrong assignment of a source on Papua New Guinea to a North-American language.
}
GC_CORRECTIONS = {
    'Ossetian (Iron)': 'iron1242',
    'Otomaco': 'otom1301',
    'Mazahua': 'cent2144',
    'Anii': 'anyi1245',
    'Burunge': 'buru1320',
}


class Dataset(pyglottography.Dataset):
    dir = pathlib.Path(__file__).parent
    id = "carling2025diacl"

    def get(self, url, refresh=False):
        url = 'https://diacl.uni-frankfurt.de/' + url
        purl = urllib.parse.urlparse(url)
        path = self.raw_dir / purl.path.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        #if refresh or (not path.exists()):
        #    urllib.request.urlretrieve(url, path)
        return path

    def cmd_download(self, args):
        geofeatures, mdfeatures = [], []
        for i, lg in enumerate(reader(self.get('Language/CSV/List', refresh=True), delimiter=';', dicts=True)):
            md = load(self.get('Language/JSON/' + lg['LanguageId'], refresh=True))
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
                    sources |= {d['FkSourceId']} if isinstance(d['FkSourceId'], int) else set(d['FkSourceId'])
                sources = [SOURCES[s] for s in sources if SOURCES[s]]
                sources = ' '.join(sorted(sources))
                geojson_path = self.get('GeographicalPresence/GeoJSON/' + gpid, refresh=True)
                feature = load(geojson_path)
                if geojson_path.stat().st_size > 1000000:
                    feature['geometry'] = simplify(shape(feature['geometry']), tolerance=0.005).__geo_interface__
                shapely_fixed_geometry(feature)
                del feature['crs']
                if 'bbox' in feature['geometry']:
                    del feature['geometry']['bbox']
                feature['properties'].update(
                    name=lg['Name'], year=year, id=gpid, map_name_full=sources)
                geofeatures.append(feature)
                mdfeatures.append(collections.OrderedDict([
                    ('id', gpid),
                    ('name', lg['Name']),
                    ('glottocode', GC_CORRECTIONS.get(lg['Name'], lg['Glottocode'])),
                    ('year', year),
                    ('map_name_full', ''),
                    ('sources', sources),
                ]))

        dump(feature_collection(geofeatures), self.raw_dir / 'dataset.geojson')
        with UnicodeWriter(self.etc_dir / 'features.csv') as writer:
            writer.writerows(sorted(mdfeatures, key=lambda f: int(f['id'])))

    def make_contribution_feature(self,
                                  args,
                                  pid: str,
                                  gc: typing.Optional[str],
                                  f: Feature,
                                  fmd: FeatureSpec,
                                  map_ids) -> dict:
        res = pyglottography.Dataset.make_contribution_feature(self, args, pid, gc, f, fmd, map_ids)
        res['Source'] = res['Source'] + fmd.properties['sources'].split()
        return res
