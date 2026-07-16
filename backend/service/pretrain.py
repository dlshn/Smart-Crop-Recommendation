"""Pre-trains and caches a price model for every crop in meta.json, plus the
shared all-crops fallback model, so the live /predict endpoint only ever
does fast inference from a cached .joblib file instead of training on
request.

Run once (and again whenever dataset.csv or meta.json changes):
    python -m service.pretrain
"""
import json
import os
import time

from service.model_service import load_model, BASE_DIR

META_PATH = os.path.join(BASE_DIR, '..', 'data', 'meta.json')


def main():
    with open(META_PATH, 'r', encoding='utf-8') as f:
        meta = json.load(f)
    crops = meta['crops']

    print(f'Pre-training shared all-crops fallback model...')
    t0 = time.time()
    load_model(crop=None)
    print(f'  done in {time.time() - t0:.1f}s')

    for i, crop in enumerate(crops, 1):
        t0 = time.time()
        load_model(crop=crop)
        print(f'[{i}/{len(crops)}] {crop}: done in {time.time() - t0:.1f}s')

    print('All models cached.')


if __name__ == '__main__':
    main()
