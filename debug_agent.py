import sys
sys.path.insert(0, '.')
from eval.sample_data import paper1, paper2
from lit_contradict.core.pipeline import ContradictionPipeline
from eval.runner import EvaluationRunner

pipeline = ContradictionPipeline(max_claims_per_paper=15, max_contradictions=10)
result = pipeline.run(paper1, paper2)
print('Pipeline contradictions:')
for c in result['contradictions']:
    print(' -', c.id, '|', c.contradiction_type, '|', c.claim_a_id[:20], '|', c.claim_b_id[:20])

# Now test the runner
runner = EvaluationRunner('eval/ground_truth.json')
agent_result = runner.run_agent()
print()
print('Agent evaluation result:')
print(' - Precision:', agent_result.precision)
print(' - Recall:', agent_result.recall)
print(' - F1:', agent_result.f1_score)
print(' - Execution time:', agent_result.execution_time_seconds)
PYEOF