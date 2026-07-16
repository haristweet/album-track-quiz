# 既存アーティストの全スタジオアルバム化（既存エントリを差し替える）
# 既存の手打ちデータには曲の抜けがあった（Violator に Blue Dress が無い等）ので
# 収録曲もすべて配信データで作り直す。色は既存の指定を引き継ぐ。
CURATION = [
    ("Kraftwerk", ["#ff2e2e", "#0b0b0b"], "US", [
        ("Autobahn", 1974, 726154713, {}),
        ("Radio-Activity", 1975, 700049905, {}),
        ("Trans-Europe Express", 1977, 726144557, {}),
        ("The Man-Machine", 1978, 726157248, {}),
        ("Computer World", 1981, 830083942, {}),
        # 2009年リマスターで追加された House Phone を落とし1986年の Electric Café 6曲に戻す
        ("Electric Café", 1986, 830083406, {"drop": ["House Phone"]}),
        ("Tour de France", 2003, 726341054, {}),
    ]),
    ("Daft Punk", ["#c9a227", "#1a1a1a"], "US", [
        ("Homework", 1997, 696884422, {}),
        ("Discovery", 2001, 697194953, {}),
        ("Human After All", 2005, 693748807, {}),
        ("Random Access Memories", 2013, 617154241, {}),
    ]),
    ("Depeche Mode", ["#b30000", "#101010"], "US", [
        ("Speak & Spell", 1981, 665396776, {}),
        ("A Broken Frame", 1982, 665410900, {}),
        ("Construction Time Again", 1983, 665403451, {}),
        ("Some Great Reward", 1984, 665403327, {}),
        ("Black Celebration", 1986, 665403454, {"take": 11}),      # 12曲目以降はボーナス
        ("Music for the Masses", 1987, 665403347, {}),
        ("Violator", 1990, 665404621, {}),
        ("Songs of Faith and Devotion", 1993, 665404898, {}),
        ("Ultra", 1997, 665404026, {}),
        ("Exciter", 2001, 665413307, {}),
        ("Playing the Angel", 2005, 665306622, {}),
        ("Sounds of the Universe", 2009, 665311619, {"take": 13}),  # 14曲目はボーナス
        ("Delta Machine", 2013, 594094332, {}),
        ("Spirit", 2017, 1199982236, {}),
        ("Memento Mori", 2023, 1670265523, {}),
    ]),
    ("New Order", ["#1f6feb", "#0d0d0d"], "US", [
        ("Movement", 1981, 1040982031, {}),
        ("Power, Corruption & Lies", 1983, 1040981945, {}),
        ("Low-Life", 1985, 1041433918, {}),
        ("Brotherhood", 1986, 1040972118, {}),
        ("Technique", 1989, 1040968369, {}),
        ("Republic", 1993, 1040965893, {}),
        ("Get Ready", 2001, 282971689, {}),
        ("Waiting for the Sirens' Call", 2005, 1041432291, {}),
        ("Music Complete", 2015, 1004091343, {}),
    ]),
    # Drukqs と Selected Ambient Works Volume II は Apple で配信されておらず収録できない
    ("Aphex Twin", ["#19c37d", "#0a0a0a"], "US", [
        ("Selected Ambient Works 85-92", 1992, 1668862636, {}),
        ("...I Care Because You Do", 1995, 281829991, {}),
        ("Richard D. James Album", 1996, 281111401, {}),
        ("Syro", 2014, 911319255, {}),
    ]),
]
