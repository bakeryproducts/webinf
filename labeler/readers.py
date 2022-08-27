import json
import datetime
from pathlib import Path


class _Annotation:
    def __init__(self, filename, info=None):
        filename = Path(filename)
        self.filename = filename.with_suffix('')
        self.info = info


class PamReader(_Annotation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _read_ann(self, filename):
        with open(str(filename), 'r') as f:
            data = json.load(f)

        polys = []
        for ann in data:
            poly = ann['geometry']['coordinates'][0]
            scaled_poly = []
            for point in poly:
                point[0], point[1] = -point[1]/64,point[0]/64
                scaled_poly.append(point)
            polys.append(scaled_poly)

        return polys

    def __call__(self):
        polys = []
        files = self.filename.parent.glob(f"{self.filename.stem}*.json")
        files = sorted(list(files))[::-1]
        print('Annotation files: ', files)
        if files:
            f = files[0]
            if f.exists():
                polys.append(self._read_ann(f))
        return polys


class PamWriter(_Annotation):
    def _create_ann(self, data):
        # data is list of polys
        fixed_polys = []
        for i, poly in enumerate(data):
            converted_poly = []
            for x, y in poly:
                # convert from latlon to pixels, dunno why, project in ([lat, lon], zoom) also works
                x = x * 64
                y = -1 * y * 64
                converted_poly.append([x,y])
            poly = dict(geometry=dict(coordinates=[converted_poly]))
            fixed_polys.append(poly)

        timestamp = '{:%Y_%b_%d_%H_%M_%S}'.format(datetime.datetime.now())
        filename = '/mnt/data' / self.filename.parent / (self.filename.stem + "|" + timestamp + '.json')
        print(f'Saving annotations at {filename}')
        with open(str(filename), 'w') as f:
            json.dump(fixed_polys, f, indent=4)
        return
