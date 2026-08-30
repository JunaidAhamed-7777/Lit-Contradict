import json
from pathlib import Path
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json

# Load AST extraction
ast = json.loads(Path('graphify-out/.graphify_ast.json').read_text(encoding='utf-8'))

# Create empty semantic extraction
sem = {
    'nodes': [],
    'edges': [],
    'hyperedges': [],
    'input_tokens': 0,
    'output_tokens': 0,
}

# Merge: AST nodes first, semantic nodes deduplicated by id
seen = {n['id'] for n in ast['nodes']}
merged_nodes = list(ast['nodes'])
for n in sem['nodes']:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])

merged_edges = ast['edges'] + sem['edges']
merged_hyperedges = sem.get('hyperedges', [])
merged = {
    'nodes': merged_nodes,
    'edges': merged_edges,
    'hyperedges': merged_hyperedges,
    'input_tokens': sem.get('input_tokens', 0),
    'output_tokens': sem.get('output_tokens', 0),
}
Path('graphify-out/.graphify_extract.json').write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Merged: {len(merged_nodes)} nodes, {len(merged_edges)} edges ({len(ast["nodes"])} AST + {len(sem["nodes"])} semantic)')

# Build graph
G = build_from_json(merged)
print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges')

# Cluster
communities = cluster(G)
cohesion = score_all(G, communities)
print(f'Communities: {len(communities)}')

# God nodes
gods = god_nodes(G)
print(f'God nodes: {gods}')

# Surprising connections
surprises = surprising_connections(G, communities)
print(f'Surprises: {surprises}')

# Save analysis
analysis = {
    'communities': {str(k): v for k, v in communities.items()},
    'cohesion': {str(k): v for k, v in cohesion.items()},
    'gods': gods,
    'surprises': surprises,
}
Path('graphify-out/.graphify_analysis.json').write_text(json.dumps(analysis, indent=2, ensure_ascii=False), encoding='utf-8')

# Generate report
labels = {cid: 'Community ' + str(cid) for cid in communities}
questions = suggest_questions(G, communities, labels)
tokens = {'input': merged.get('input_tokens', 0), 'output': merged.get('output_tokens', 0)}
detection = json.loads(Path('graphify-out/.graphify_detect.json').read_text(encoding='utf-8'))

report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report, encoding='utf-8')

# Export graph JSON
to_json(G, communities, 'graphify-out/graph.json')
print('Graph complete!')