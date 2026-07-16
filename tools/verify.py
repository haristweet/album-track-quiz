#!/usr/bin/env python3
"""index.html のデータを検証する。

    python3 tools/verify.py            # データの整合性のみ
    python3 tools/verify.py --covers   # ジャケットURLの死活確認もする（全枚数にHEADを投げる）

問題があれば終了コード1で落ちる。
"""
import argparse
import concurrent.futures
import os
import re
import sys
import urllib.request

HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'index.html')
MAX_TRACKS = 18

# 直しようがないと分かっている例外。増やす前に本当に直せないか確認すること。
KNOWN_NO_COVER = {
    # 1990年の作品で Apple Music に配信自体が無く、ジャケットを取得できない。
    # drawCover() の自動生成画で表示される。
    '電気グルーヴ||662 BPM BY DG',
}

_ALBUM = re.compile(r'\{ title:"((?:[^"\\]|\\.)*)", year:(\d+), tracks:\[(.*?)\] \},')
_STR = re.compile(r'"(?:[^"\\]|\\.)*"')


def parse(html):
    """[(アーティスト, [(タイトル, 年, 曲数), ...]), ...] と COVERS の dict を返す。"""
    db = html.split('const DB = [')[1].split('\n];')[0]
    artists = []
    for chunk in db.split(' { artist:"')[1:]:
        name = chunk.split('"')[0]
        albums = [(m.group(1), int(m.group(2)), len(_STR.findall(m.group(3))))
                  for m in _ALBUM.finditer(chunk)]
        artists.append((name, albums))
    covers = dict(re.findall(r'^  "(.*?)": "(https?://.*?)",$', html, re.M))
    return artists, covers


def http_ok(item):
    key, url = item
    try:
        req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            return (key, r.status)
    except Exception as e:
        return (key, 'ERR %s' % e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--covers', action='store_true', help='ジャケットURLにHEADを投げて死活確認する')
    args = ap.parse_args()

    html = open(HTML).read()
    artists, covers = parse(html)
    problems = []

    n_albums = sum(len(a[1]) for a in artists)
    n_tracks = sum(t for _, albums in artists for *_, t in albums)
    print('アーティスト %d / アルバム %d / 総曲数 %d / ジャケット %d'
          % (len(artists), n_albums, n_tracks, len(covers)))

    seen = set()
    for name, albums in artists:
        if name in seen:
            problems.append('アーティストが重複: %s' % name)
        seen.add(name)
        if len(albums) <= 2:
            problems.append('アルバムが%d枚しかなく、おとりの幅が足りない: %s' % (len(albums), name))
        titles = set()
        for title, year, ntracks in albums:
            key = name + '||' + title
            if title in titles:
                problems.append('アルバムが重複: %s' % key)
            titles.add(title)
            if ntracks >= MAX_TRACKS:
                problems.append('収録曲が%d曲で上限%d超過: %s' % (ntracks, MAX_TRACKS, key))
            if key not in covers and key not in KNOWN_NO_COVER:
                problems.append('ジャケット未設定（自動生成の代替画になる）: %s' % key)

    if args.covers:
        with concurrent.futures.ThreadPoolExecutor(16) as ex:
            for key, status in ex.map(http_ok, covers.items()):
                if status != 200:
                    problems.append('ジャケットが取得できない (%s): %s' % (status, key))
        print('ジャケットURL %d 件の死活確認を実施' % len(covers))

    if problems:
        print('\n要確認 %d 件:' % len(problems))
        for p in problems:
            print('  -', p)
        sys.exit(1)
    print('\n問題なし')


if __name__ == '__main__':
    main()
