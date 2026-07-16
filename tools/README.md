# tools — 出題データのメンテナンス

`index.html` の `DB`（アーティストとアルバムの収録曲）と `COVERS`（ジャケット画像URL）を
iTunes Search API から生成する。**収録曲は手で打たないこと。**
過去に手打ちしていた頃は曲の抜けが10枚分あった（Daft Punk の Homework が8曲しか入って
おらず正しくは16曲、Depeche Mode の Violator から Blue Dress が欠落、など）。
曲名そのものが答えのクイズなので、データの正確さがそのまま正誤判定の正しさになる。

## アーティストを追加する

### 1. アルバムを調べる

APIは「どれがスタジオアルバムか」を教えてくれない。シングル・EP・リミックス盤・ライブ盤・
デラックス版・サントラが同じ一覧に混ざって返る（Underworld は88件返ってくる）。
まず候補を目で見る:

```python
python3 -c "
import sys; sys.path.insert(0,'tools')
from itunes import find_artist, albums
print(find_artist('Underworld'))          # -> artistId を得る
for a in albums(996876):
    print(a['id'], a['year'], a['n'], a['name'])
"
```

### 2. curation ファイルを書く

`curation/` に手で選別した結果を置く。書式:

```python
CURATION = [
    (アーティスト表示名, [色_前景, 色_背景], ストア, [
        (アルバム表示名, 発表年, collectionId, オプション),
        ...
    ]),
]
```

オプションは配信版と正規盤がズレているときに使う:

- `{"take": 12}` — 先頭12曲だけ採用（末尾に配信版のボーナス曲が付いている場合）
- `{"drop": ["House Phone"]}` — 曲名を指定して除外（曲の途中に再発の追加曲がある場合）

### 3. 反映して検証する

```bash
python3 tools/build.py tools/curation/06_new_artists.py   # index.html を更新
python3 tools/verify.py --covers                          # 整合性とジャケットの死活確認
```

`build.py` は curation のアーティストが既に `index.html` にいれば同じ位置で差し替え、
いなければ末尾に追加する。既存アーティストのアルバムを増やすときも同じ手順でよい。

最後にブラウザで通しプレイして確認する（`.claude/launch.json` の `album-quiz`、ポート8780）。

## 収録するかどうかの判断基準

- **収録曲18曲以上のアルバムは入れない**（`build.py` が自動で弾く）。
  おとりの数が `makeRound()` の `Math.min(7, ...)` で7曲に頭打ちになるので、収録曲が
  多いアルバムほど「選択肢を全部選ぶ」だけで高得点が取れてしまう。26曲のアルバムだと
  満点の73%が取れる。**おとりの数を収録曲数に比例させる仕様に直せばこの上限は不要になり、
  Geogaddi などの名盤も収録できるようになる。**
- **1アーティストにつき最低3枚**。おとりは同じアーティストの別アルバムから作るので、
  2枚しかないとおとりの幅が足りずクイズとして成立しない。
  （Boards of Canada は代表作2枚が18曲上限に掛かり、この理由で収録を見送っている）
- ミックス盤・リミックス盤・ライブ盤・EP・ベスト盤・別名義は入れない。

## API の落とし穴

- **洋楽は `US`、邦楽は `JP` ストアから取る。** JPストアだと洋楽の曲名がカタカナ化される
  （Born in the Echoes が「ゴー (feat. Qティップ)」になる）。
- **発表年はAPIを信用せず手で書く。** 再発盤はメタデータの年が原盤とズレる
  （砂原良徳の LOVEBEAT は2001年だがAPIは1999年、Jean-Michel Jarre の Rendez-Vous は
  1986年だがAPIは2015年を返す）。
- **配信版にはボーナス曲が混ざる。** "Bonus Track" と名前に付いていれば自動で落とすが、
  Chemical Brothers の We Are the Night のように無印で紛れ込む場合は `take` で切る。
- 配信されていないアルバムは収録できない。Aphex Twin の Drukqs、Tangerine Dream の
  Rubycon、Vangelis の Blade Runner、Giorgio Moroder の E=MC²、電気グルーヴの
  662 BPM BY DG などが該当する。
