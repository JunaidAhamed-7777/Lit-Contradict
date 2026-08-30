import sys, json
from graphify.extract import collect_files, extract
from pathlib import Path
import json

detect_content = """{
  "files": {
    "code": [
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\cli.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\data\\__init__.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\debug_agent.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\eval\\baseline.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\eval\\ground_truth.json",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\eval\\runner.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\eval\\sample_data.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\__init__.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\agents\\__init__.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\agents\\comparator.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\agents\\extractor.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\agents\\verifier.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\api\\__init__.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\api\\server.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\core\\__init__.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\core\\pipeline.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\core\\schemas.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\tools\\graph_construction.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\tools\\pdf_fetch.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\tools\\pdf_parse.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\lit_contradict\\tools\\text_processing.py",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\test_comp2.py"
    ],
    "document": [
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\README.md",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\ascii-art.txt",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\plan.md",
      "C:\\aaFiles\\aaGithub\\Lit-Contradict\\requirements.txt"
    ]
  },
  "total_files": 26,
  "total_words": 12025
}"""

detect = json.loads(detect_content)
code_files = []
for f in detect.get('files', {}).get('code', []):
    code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)])

if code_files:
    result = extract(code_files, cache_root=Path('.'))
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f'AST: {len(result["nodes"])} nodes, {len(result["edges"])} edges')
else:
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}, ensure_ascii=False), encoding="utf-8")
    print('No code files - skipping AST extraction')