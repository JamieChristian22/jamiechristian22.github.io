"""Inject fixed, approved synthetic analytics into a single offline HTML demo."""
from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
template=root/'demo/index.html'
report=json.loads((root/'reports/advanced_metrics.json').read_text())
s=template.read_text()
marker='/*ADVANCED_JSON*/'
if marker not in s:
    # For subsequent builds the data is already embedded and remains static.
    print('Offline dashboard already includes metrics')
else:
    s=s.replace(marker,json.dumps(report,ensure_ascii=False).replace('</','<\\/'))
    template.write_text(s)
    print('Embedded reproducible cohort and duration metrics in '+str(template))
