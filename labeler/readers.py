import json
from pathlib import Path

class _Annotation:
    def __init__(self, filename, info=None):
        filename = Path(filename)
        self.filename = filename
        self.info = info

class PamReader(_Annotation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self):
        with open(str(self.filename), 'r') as f:
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


