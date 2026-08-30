from graphify.detect import detect
from pathlib import Path
import json

r = detect(Path('.'))
with open('graphify-out/.graphify_detect.json', 'w', encoding='utf-8') as f:
    json.dump(r, f, ensure_ascii=False)
print(f'Files: {r["total_files"]}, Words: {r["total_words"]}')
print(f'Code: {len(r["files"]["code"])}')
print(f'Docs: {len(r["files"]["document"])}')
print(f'Skipped: {r["skipped_sensitive"]}')