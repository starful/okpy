# A8 掲載URL（okpy）

**プログラム単位管理:** [`/opt/work/data/a8/`](../../../data/a8/README.md)

| プログラム | ID | CSV（このフォルダ / ハブ同一内容） |
|------------|-----|-------------------------------------|
| Neuro Dive | `s00000019630003` | `s00000019630003.csv` |
| @PRO人 | `s00000020853002` | `s00000020853002.csv` |

```bash
python3 scripts/generate_a8_placement_urls.py
# または
python3 /opt/work/data/a8/generate_placement_urls.py -p neuro_dive
```

A8 アップロードは **プログラムID名の CSV** を使います。Neuro Dive は starful.biz URL も含みます。
