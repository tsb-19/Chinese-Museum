# Data pipeline notes

- Source of truth currently: `Chinese Museum.xlsx`
- Pipeline entrypoint: `python scripts/build.py`

## Script roles
- `export_xlsx_to_json.py`: export first worksheet into `data/artifacts.json`
- `validate_data.py`: validate required fields and basic URL formatting
- `update_dates.py`: sync `index.html` and `sitemap.xml` date metadata
- `generate_sitemap.py`: generate `sitemap.xml` from dataset (home + museum anchors)
