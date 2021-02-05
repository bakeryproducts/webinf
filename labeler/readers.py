import json
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

        allowable_postfixes = ['_ell.json', '.json']
        for postfix in allowable_postfixes:
            filename = self.filename.with_suffix('')
            filename = str(filename) + postfix
            if Path(filename).exists():
                polys.append(self._read_ann(filename))

        return polys

