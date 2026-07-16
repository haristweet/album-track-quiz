"""iTunes Search API クライアント。

アーティスト検索・アルバム一覧・収録曲取得と、曲名の正規化を行う。
アルバムの選別（どれがスタジオ盤か）はAPIからは判断できないので、
curation/ 配下に手で書いたリストで指定する。
"""
import json
import re
import time
import urllib.parse
import urllib.request

_UA = {'User-Agent': 'Mozilla/5.0'}


def api(path, **params):
    url = "https://itunes.apple.com/" + path + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=_UA), timeout=25) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))


def find_artist(name, country="US"):
    """アーティスト候補を [(artistId, 名前, ジャンル), ...] で返す。"""
    d = api("search", term=name, entity="musicArtist", limit=5, country=country)
    return [(r.get('artistId'), r.get('artistName'), r.get('primaryGenreName')) for r in d['results']]


def albums(artist_id, country="US"):
    """アーティストのアルバム一覧。シングルやリミックス盤も混ざって返るので呼び出し側で選ぶ。"""
    d = api("lookup", id=artist_id, entity="album", limit=200, country=country)
    out = []
    for r in d['results']:
        if r.get('wrapperType') != 'collection':
            continue
        out.append({'id': r['collectionId'], 'name': r.get('collectionName'),
                    'year': (r.get('releaseDate') or '')[:4], 'n': r.get('trackCount'),
                    'art': r.get('artworkUrl100')})
    out.sort(key=lambda x: (x['year'], x['name']))
    return out


# 再発・配信由来のノイズだけを曲名末尾から落とす。
# "Charly (Trip Into Drum and Bass version)" のような意味のある括弧は残す。
_NOISE = re.compile(
    r'\s*[\(\[](?:[^()\[\]]*\b(?:remaster(?:ed)?|bonus track|explicit|album version'
    r'|20\d\d mix|digital remaster)\b[^()\[\]]*)[\)\]]\s*$', re.I)


def clean(title):
    """曲名を既存データの表記に揃える（活字体アポストロフィを直線に、再発サフィックス除去）。"""
    title = (title.replace('’', "'").replace('‘', "'")
                  .replace('“', '"').replace('”', '"'))
    prev = None
    while prev != title:
        prev = title
        title = _NOISE.sub('', title).strip()
    return title


def _is_bonus(title):
    return bool(re.search(r'\bbonus track\b', title, re.I))


def tracks(collection_id, country="US", drop_bonus=True):
    """アルバムの収録曲を曲順で返す。"""
    d = api("lookup", id=collection_id, entity="song", limit=200, country=country)
    ts = []
    for r in d['results']:
        if r.get('wrapperType') != 'track':
            continue
        name = r.get('trackName') or ''
        if drop_bonus and _is_bonus(name):
            continue
        ts.append((r.get('discNumber') or 1, r.get('trackNumber') or 0, clean(name)))
    ts.sort(key=lambda x: (x[0], x[1]))
    return [t[2] for t in ts]


def album_art(collection_id, country="US"):
    """ジャケット画像URL（300x300）。"""
    d = api("lookup", id=collection_id, country=country)
    for r in d['results']:
        if r.get('wrapperType') == 'collection':
            return re.sub(r'/100x100bb\.jpg$', '/300x300bb.jpg', r.get('artworkUrl100') or '')
    return None
