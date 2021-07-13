import json
import pickle
import time
import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from lapjv import lapjv
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from scipy.spatial.distance import cdist


def rand_select(es,fs, n=100):
    idxs = np.random.choice(np.arange(es.shape[0]), n, replace=False)
    return es[idxs], fs[idxs], idxs

def save_tsne_grid(img_collection, X_2d, out_res, out_dim, n):
    grid = np.dstack(np.meshgrid(np.linspace(0, 1, out_dim), np.linspace(0, 1, out_dim))).reshape(-1, 2)
    cost_matrix = cdist(grid, X_2d, "sqeuclidean").astype(np.float32)
    cost_matrix = cost_matrix * (100000 / cost_matrix.max())
    #print(cost_matrix.shape)
    row_asses, col_asses, _ = lapjv(cost_matrix)
    grid_jv = grid[col_asses]
    out = np.ones((out_dim*out_res, out_dim*out_res, 3))

    for pos, img in zip(grid_jv, img_collection[0:n]):
        h_range = int(np.floor(pos[0]* (out_dim - 1) * out_res))
        w_range = int(np.floor(pos[1]* (out_dim - 1) * out_res))
        out[h_range:h_range + out_res, w_range:w_range + out_res]  = img.numpy().transpose(1,2,0)

    #print(out.shape, out.dtype, out.max())
    im = Image.fromarray((255 * out).astype(np.uint8))
    return im, grid_jv
    #im.save(out_dir + out_name, quality=100)

    
def calc_tsne_grid(x_emb, metric='euclidean'):
    out_dim = int(x_emb.shape[0]**.5)
    grid = np.dstack(np.meshgrid(np.linspace(0, 1, out_dim), np.linspace(0, 1, out_dim))).reshape(-1, 2)
    cost_matrix = cdist(grid, x_emb, metric).astype(np.float32)
    #cost_matrix = cost_matrix / cost_matrix.max()
    row_asses, col_asses, _ = lapjv(cost_matrix)
    grid_jv = grid[col_asses] * (out_dim-1)
    grid_jv = grid_jv.round().astype(np.int32)
    return grid_jv
    
def read_labels_idxs(path, idxs, mask='labels_*.csv'):
    files = Path(path).glob(mask)
    labels = {}
    for f in files:
        all_labels = pd.read_csv(str(f), index_col=None, header=None).values.flatten()
        labels[f.name] = all_labels[idxs]
    
    return labels


def nearest_select(embeddings, filenames, n, key_name):
    assert key_name in filenames, (key_name, filenames[:2])
    i = filenames.tolist().index(key_name)
    e = embeddings[i]
    ds = cdist(embeddings, e[None,:]).flatten()
    idxs = np.argsort(ds)[:n]
    assert i in idxs, (i, idxs)
    return embeddings[idxs], filenames[idxs], idxs


def generate_projection(src, n, tile_size, path_prefix='', proj_name=None, metric='euclidean', selector='rand', **kwargs):
    N_SUB = n
    METRIC = metric
    TILE_SIZE = tile_size
    proj_dst = src / (f'{N_SUB}_' + '{:%b_%d_%H_%M_%S}'.format(datetime.datetime.now())) if proj_name is None else proj_name
    proj_dst.mkdir()

    embeddings = np.load(str(src/'e.npy'))
    filenames = pd.read_csv(str(src/'imgs.csv'), index_col=None, header=None).values.flatten()
    if selector == 'rand':
        embeddings,filenames, idxs = rand_select(embeddings, filenames, N_SUB)
    elif selector == 'nearest':
        embeddings,filenames, idxs = nearest_select(embeddings, filenames, N_SUB, **kwargs)

    labels = read_labels_idxs(src, idxs)

    pca = PCA(n_components=100)
    embs_pca = pca.fit_transform(embeddings)
    tsne = TSNE(n_components=2, n_jobs=-1)
    embs_tsne = tsne.fit_transform(embs_pca)
    embs_tsne -= embs_tsne.min(axis=0)
    embs_tsne /= embs_tsne.max(axis=0)

    xy = calc_tsne_grid(embs_tsne, metric=METRIC)

    ks,vs = [],[]
    for k,v in labels.items():
        ks.append(k)
        vs.append(v)
        
    if labels:
        xx = np.hstack([xy, np.array(vs).T])
    else:
        xx = xy

    df = pd.DataFrame(xx, columns=['x', 'y', *ks], index=idxs)
    df[['x', 'y']] = df[['x', 'y']].astype(int)
    df['fn'] = filenames

    d = {
        'n':N_SUB,
        'proj':'proj.csv',
        'width':TILE_SIZE*int(N_SUB**.5),
        'height':TILE_SIZE*int(N_SUB**.5),
        'lap_metric':METRIC,
        'tile_size':TILE_SIZE,
        'path_prefix': str(path_prefix),
    }

    df.to_csv(str(proj_dst / 'proj.csv'))

    tsne_path = proj_dst / 'tsne.pkl'
    with open(str(tsne_path), 'wb') as f:
        pickle.dump(tsne, f)

    pca_path = proj_dst / 'pca.pkl'
    with open(str(pca_path), 'wb') as f:
        pickle.dump(pca, f)

    e_path = proj_dst/'prj.json'
    with open(str(e_path), 'w') as f:
        json.dump(d, f, indent=4)

    return e_path


