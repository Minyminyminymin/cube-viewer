"""Replace the DATA block inside cube_trajectory_viewer.html with a JSON file made by build_viewer_data.py."""
import json, sys
html, data = sys.argv[1], sys.argv[2]
h = open(html, encoding='utf-8').read()
i = h.index('const DATA=') + len('const DATA='); _, end = json.JSONDecoder().raw_decode(h[i:])
new = open(data, encoding='utf-8').read(); json.loads(new)
open(html, 'w', encoding='utf-8').write(h[:i] + new + h[i + end:])
print('embedded', len(new), 'chars of data into', html)
