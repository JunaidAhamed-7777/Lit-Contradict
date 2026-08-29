import sys
sys.path.insert(0, '.')
from eval.sample_data import paper1, paper2
from lit_contradict.agents.extractor import ExtractorAgent
from lit_contradict.agents.comparator import ComparatorAgent

extractor = ExtractorAgent()
comparator = ComparatorAgent()

claims_a = extractor.extract(paper1)
claims_b = extractor.extract(paper2)

print('Claims from paper1:', len(claims_a))
print('Claims from paper2:', len(claims_b))

# Try all pairs
for ca in claims_a:
    for cb in claims_b:
        result = comparator.compare_claims(ca, cb)
        if result is not None:
            print('Contradiction found:')
            print('  Type:', result.contradiction_type)
            print('  Explanation:', result.explanation[:80])
            print('  Confidence:', result.confidence_score)
            print('  A:', ca.normalized_claim_text[:50])
            print('  B:', cb.normalized_claim_text[:50])
            print()