#!/usr/bin/env python3
"""curation ファイルを読んで index.html の DB / COVERS を更新する。

    python3 tools/build.py tools/curation/01_uk_dance.py
    python3 tools/build.py tools/curation/*.py --dry-run

curation に書いたアーティストが index.html に既にいれば同じ位置で差し替え、
いなければ末尾に追加する。収録曲とジャケットはすべて iTunes Search API から
取り直すので、手打ちによる曲の抜けが入り込まない。
"""
import argparse
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import itunes  # noqa: E402

HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'index.html')

# 収録曲がこれ以上のアルバムは出題対象にしない。
# おとりの数が makeRound() の Math.min(7, ...) で7曲に頭打ちになるため、収録曲が
# 多いアルバムほど「選択肢を全部選ぶ」だけで高得点が取れてしまう（26曲なら満点の73%）。
# おとりの数を収録曲数に比例させる仕様に直せば、この上限は不要になる。
MAX_TRACKS = 18


def load_curation(path):
    spec = importlib.util.spec_from_file_location('curation', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CURATION


def build_artist(artist, color, country, items):
    """1アーティスト分の DB ブロックと COVERS 行を組み立てる。"""
    db = [' { artist:"%s", color:["%s","%s"], albums:[' % (artist, color[0], color[1])]
    covers, notes = [], []
    for title, year, cid, opts in items:
        ts = itunes.tracks(cid, country=country)
        if 'drop' in opts:
            ts = [t for t in ts if t not in opts['drop']]
        if 'take' in opts:
            ts = ts[:opts['take']]
        if not ts:
            notes.append('  !! 曲データが取得できない: %s / %s (%s)' % (artist, title, cid))
            continue
        if len(ts) >= MAX_TRACKS:
            notes.append('  -- 収録曲%d曲で上限超過のため除外: %s / %s' % (len(ts), artist, title))
            continue
        db.append('   { title:%s, year:%d, tracks:[%s] },' % (
            json.dumps(title, ensure_ascii=False), year,
            ','.join(json.dumps(t, ensure_ascii=False) for t in ts)))
        art = itunes.album_art(cid, country)
        if art:
            covers.append('  %s: %s,' % (json.dumps(artist + '||' + title, ensure_ascii=False),
                                         json.dumps(art, ensure_ascii=False)))
        else:
            notes.append('  !! ジャケットが取得できない: %s / %s' % (artist, title))
        notes.append('  %-40s %s  %2d曲' % (title[:40], year, len(ts)))
    db.append(' ]},')
    return '\n'.join(db), covers, notes


def upsert(html, artist, block, covers):
    """既存アーティストなら同じ位置で差し替え、新規なら DB の末尾に追加する。"""
    pat = re.compile(r' \{ artist:"' + re.escape(artist) + r'", color:\[.*?\], albums:\[\n.*?\n \]\},', re.S)
    if pat.search(html):
        html = pat.sub(lambda m: block, html, count=1)
        html = re.sub(r'^  "' + re.escape(artist) + r'\|\|[^"]*": "[^"]*",\n', '', html, flags=re.M)
        action = '差し替え'
    else:
        end = html.index('\n];\n', html.index('const DB = ['))
        html = html[:end] + '\n' + block + html[end:]
        action = '追加'
    end = html.index('\n};\n', html.index('const COVERS = {'))
    html = html[:end] + '\n' + '\n'.join(covers) + html[end:]
    return html, action


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('curation', nargs='+')
    ap.add_argument('--dry-run', action='store_true', help='index.html を書き換えず内容だけ表示する')
    args = ap.parse_args()

    html = open(HTML).read()
    for path in args.curation:
        print('### %s' % os.path.basename(path))
        for artist, color, country, items in load_curation(path):
            block, covers, notes = build_artist(artist, color, country, items)
            print('\n'.join(notes))
            html, action = upsert(html, artist, block, covers)
            print('  -> %s: %s' % (action, artist))
    if args.dry_run:
        print('\n(--dry-run のため index.html は変更していない)')
        return
    open(HTML, 'w').write(html)
    print('\nindex.html を更新した。tools/verify.py で検証すること。')


if __name__ == '__main__':
    main()
