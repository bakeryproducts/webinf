import json
from pathlib import Path

import numpy as np


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
        for j in data:
            p = j['geometry']['coordinates'][0]
            p = np.array(p)
            p[:,1]*=-1
            p = p[:,::-1]/64
            p = p.tolist()
            polys.append(p)

        return polys


