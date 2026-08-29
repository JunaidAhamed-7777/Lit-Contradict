"""Sample ground-truth dataset for contradiction detection.

This module provides complete academic paper data with full text content
for baseline and agent benchmarking. Each paper has non-empty full_text,
abstract, and relevant section headers (Methods, Results, Discussion).

The ground-truth contains 5 evaluation pairs with explicit, verifiable
claim pairs containing exact quote references corresponding directly
to the populated paper texts.
"""

import json
from lit_contradict.core.schemas import Paper, Claim, Contradiction


# ============================================================
# Complete Paper Objects with Full Text Content
# ============================================================

# Paper 1: Empirical study on drug efficacy
paper1 = Paper(
    id="paper1",
    title="A Randomized Controlled Trial of Drug X for Hypertension",
    authors=["Dr. Alice Roberts", "Dr. Benjamin Chen"],
    abstract="Hypertension affects over 1 billion people worldwide. This randomized controlled trial evaluated the efficacy and safety of Drug X compared to a standard placebo treatment over a 12-week period. Our primary endpoint was systolic blood pressure reduction.",
    full_text="""Hypertension affects over 1 billion people worldwide. This randomized controlled trial evaluated the efficacy and safety of Drug X compared to a standard placebo treatment over a 12-week period. 

Our primary endpoint was systolic blood pressure reduction. METHODS: We enrolled 200 patients with Stage 1-2 hypertension and randomized them to receive either Drug X (20mg daily) or a matching placebo. Blood pressure was measured at baseline, 4, 8, and 12 weeks using a validated sphygmomanometer. 

RESULTS: At week 12, the Drug X group showed a mean systolic blood pressure reduction of 28.5 mmHg (SD 8.2), while the placebo group showed a reduction of 12.3 mmHg (SD 9.1). The difference between groups was statistically significant (p < 0.001). Secondary endpoints included diastolic blood pressure, heart rate, and adverse events. 

DISCUSSION: The observed 16.2 mmHg greater reduction in the Drug X group is clinically meaningful. Approximately 65% of Drug X patients achieved target blood pressure (<140/90 mmHg) compared to 35% in the placebo group. The most common adverse event was mild headache occurring in 8% of Drug X recipients. 

CONCLUSION: Drug X 20mg once daily provides significant additional blood pressure reduction compared to placebo in patients with Stage 1-2 hypertension over 12 weeks. These findings support its use as a first-line adjunct therapy for moderate hypertension.

Safety monitoring revealed no serious cardiovascular events. Long-term studies are warranted to assess cardiovascular outcome reductions.""",
    sections={
        "Abstract": "Hypertension affects over 1 billion people worldwide. This randomized controlled trial evaluated the efficacy and safety of Drug X compared to a standard placebo treatment over a 12-week period. Our primary endpoint was systolic blood pressure reduction.",
        "Methods": "We enrolled 200 patients with Stage 1-2 hypertension and randomized them to receive either Drug X (20mg daily) or a matching placebo. Blood pressure was measured at baseline, 4, 8, and 12 weeks using a validated sphygmomanometer.",
        "Results": "At week 12, the Drug X group showed a mean systolic blood pressure reduction of 28.5 mmHg (SD 8.2), while the placebo group showed a reduction of 12.3 mmHg (SD 9.1). The difference between groups was statistically significant (p < 0.001). Secondary endpoints included diastolic blood pressure, heart rate, and adverse events.",
        "Discussion": "The observed 16.2 mmHg greater reduction in the Drug X group is clinically meaningful. Approximately 65% of Drug X patients achieved target blood pressure (<140/90 mmHg) compared to 35% in the placebo group. The most common adverse event was mild headache occurring in 8% of Drug X recipients.",
        "Conclusion": "Drug X 20mg once daily provides significant additional blood pressure reduction compared to placebo in patients with Stage 1-2 hypertension over 12 weeks. These findings support its use as a first-line adjunct therapy for moderate hypertension.",
    },
)

# Paper 2: Contradictory empirical study (lower efficacy)
paper2 = Paper(
    id="paper2",
    title="A Double-Blind Study of Drug X for Mild Hypertension",
    authors=["Dr. Carla Smith", "Dr. David Park"],
    abstract="This double-blind study examined Drug X efficacy in mild hypertension patients over 6 weeks. We hypothesized similar blood pressure reductions to the prior 12-week trial but in a shorter timeframe.",
    full_text="""This double-blind study examined Drug X efficacy in mild hypertension patients over 6 weeks. We hypothesized similar blood pressure reductions to the prior 12-week trial but in a shorter timeframe. 

METHODS: We enrolled 150 patients with mild hypertension (systolic 140-159 mmHg) and randomized them to receive either Drug X (20mg daily) or a matching placebo. Blood pressure was measured at baseline, 3, and 6 weeks. 

RESULTS: At week 6, the Drug X group showed a mean systolic blood pressure reduction of 8.7 mmHg (SD 5.3), while the placebo group showed a reduction of 7.1 mmHg (SD 4.8). The difference between groups was NOT statistically significant (p = 0.12). 

DISCUSSION: The 1.6 mmHg greater reduction in the Drug X group was smaller than expected and did not reach statistical significance. This contrasts with the 16.2 mmHg difference observed in the 12-week trial. The shorter duration, milder patient population, and potential placebo effect may explain the divergent results. 

CONCLUSION: Drug X 20mg once daily did not demonstrate statistically significant blood pressure reduction over 6 weeks in mild hypertension patients. The drug may require longer treatment duration or higher doses for clinical effect in mild cases.

No serious adverse events were reported. Mild dizziness occurred in 5% of participants.""",
    sections={
        "Abstract": "This double-blind study examined Drug X efficacy in mild hypertension patients over 6 weeks. We hypothesized similar blood pressure reductions to the prior 12-week trial but in a shorter timeframe.",
        "Methods": "We enrolled 150 patients with mild hypertension (systolic 140-159 mmHg) and randomized them to receive either Drug X (20mg daily) or a matching placebo. Blood pressure was measured at baseline, 3, and 6 weeks.",
        "Results": "At week 6, the Drug X group showed a mean systolic blood pressure reduction of 8.7 mmHg (SD 5.3), while the placebo group showed a reduction of 7.1 mmHg (SD 4.8). The difference between groups was NOT statistically significant (p = 0.12).",
        "Discussion": "The 1.6 mmHg greater reduction in the Drug X group was smaller than expected and did not reach statistical significance. This contrasts with the 16.2 mmHg difference observed in the 12-week trial. The shorter duration, milder patient population, and potential placebo effect may explain the divergent results.",
        "Conclusion": "Drug X 20mg once daily did not demonstrate statistically significant blood pressure reduction over 6 weeks in mild hypertension patients. The drug may require longer treatment duration or higher doses for clinical effect in mild cases.",
    },
)

# Paper 3: Methodological study on temperature effects
paper3 = Paper(
    id="paper3",
    title="Temperature Dependencies in Catalytic Converter Efficiency",
    authors=["Prof. Elena Vasquez", "Dr. Michael O'Connor"],
    abstract="This study investigates how operating temperature affects catalytic converter efficiency in passenger vehicles. We measured emissions across a range of engine operating conditions.",
    full_text="""Temperature Dependencies in Catalytic Converter Efficiency

Engine emissions remain a major environmental concern. This study investigates how operating temperature affects catalytic converter efficiency in passenger vehicles. We measured emissions across a range of engine operating conditions.

METHODS: We tested three catalytic converters from different manufacturers on a dynamometer across 50 driving cycles. Engine operating temperatures were systematically varied from 200°C to 800°C. Carbon monoxide (CO), nitrogen oxides (NOx), and hydrocarbon (HC) emissions were measured at each temperature point.

RESULTS: Converter A achieved peak efficiency (92% CO reduction) at 600°C. Converter B peaked at 750°C with 88% NOx reduction. Converter C showed optimal HC reduction (85%) at 550°C. Below 400°C, all converters showed efficiency drops below 70%. Above 800°C, efficiency declined due to thermal degradation.

DISCUSSION: The temperature optima vary significantly by converter design and material composition. Converter A's alumina washcoat performed best at mid-range temperatures, while Converter B's precious metal loading optimized at higher temperatures. These findings have important implications for engine calibration and emissions certification protocols.

CONCLUSION: Catalytic converter efficiency is strongly temperature-dependent, with optimal performance ranges specific to each converter design. Engine management systems should optimize warm-up strategies to reach target temperatures efficiently. Real-world driving data suggests many vehicles operate below optimal converter temperatures during cold starts.

Further research is needed to develop temperature-adaptive catalyst formulations.""",
    sections={
        "Abstract": "This study investigates how operating temperature affects catalytic converter efficiency in passenger vehicles. We measured emissions across a range of engine operating conditions.",
        "Methods": "We tested three catalytic converters from different manufacturers on a dynamometer across 50 driving cycles. Engine operating temperatures were systematically varied from 200°C to 800°C. Carbon monoxide (CO), nitrogen oxides (NOx), and hydrocarbon (HC) emissions were measured at each temperature point.",
        "Results": "Converter A achieved peak efficiency (92% CO reduction) at 600°C. Converter B peaked at 750°C with 88% NOx reduction. Converter C showed optimal HC reduction (85%) at 550°C. Below 400°C, all converters showed efficiency drops below 70%. Above 800°C, efficiency declined due to thermal degradation.",
        "Discussion": "The temperature optima vary significantly by converter design and material composition. Converter A's alumina washcoat performed best at mid-range temperatures, while Converter B's precious metal loading optimized at higher temperatures. These findings have important implications for engine calibration and emissions certification protocols.",
        "Conclusion": "Catalytic converter efficiency is strongly temperature-dependent, with optimal performance ranges specific to each converter design. Engine management systems should optimize warm-up strategies to reach target temperatures efficiently.",
    },
)

# Paper 4: Contradictory methodological study (different temperature claims)
paper4 = Paper(
    id="paper4",
    title="Optimizing Catalyst Light-Off Performance in Gasoline Vehicles",
    authors=["Prof. Daniel Kim", "Dr. Sarah Johnson"],
    abstract="This research focuses on catalyst light-off temperature reduction as a key strategy for reducing cold-start emissions. We evaluated three aftermarket catalyst formulations.",
    full_text="""Optimizing Catalyst Light-Off Performance in Gasoline Vehicles

Cold-start emissions constitute up to 80% of total daily hydrocarbon emissions in urban driving. This research focuses on catalyst light-off temperature reduction as a key strategy for reducing cold-start emissions. We evaluated three aftermarket catalyst formulations.

METHODS: We installed three different catalyst formulations on a fleet of 30 gasoline vehicles. Light-off temperature was defined as the time required to achieve 50% of maximum conversion efficiency. Vehicles were tested on a chassis dynamometer over the EPA driving cycle starting from cold ambient conditions (22°C).

RESULTS: Formulation X achieved light-off in 45 seconds. Formulation Y achieved light-off in 62 seconds. Formulation Z achieved light-off in 38 seconds. All formulations underperformed relative to the manufacturer's baseline, which achieves light-off in 25 seconds. Formulation Z showed the fastest light-off but degraded fastest after 5,000 miles.

DISCUSSION: The claimed 38-second light-off for Formulation Z is notably faster than the 62-second and 45-second results for Formulations Y and X, respectively. However, the rapid degradation after 5,000 miles raises concerns about long-term durability. The 25-second manufacturer baseline suggests that current aftermarket formulations still have significant room for improvement. Our results indicate that Formulation Z's apparent advantage may be short-lived.

CONCLUSION: While Formulation Z offers the fastest initial light-off among aftermarket options, durability concerns and poor performance relative to manufacturer baselines limit its practical value. Future research should focus on stable formulations that can consistently achieve light-off below 40 seconds without rapid degradation.

Testing confirmed Formulation Z maintained 50% efficiency for 5,000 miles, after which conversion efficiency dropped below 70%.""",
    sections={
        "Abstract": "This research focuses on catalyst light-off temperature reduction as a key strategy for reducing cold-start emissions. We evaluated three aftermarket catalyst formulations.",
        "Methods": "We installed three different catalyst formulations on a fleet of 30 gasoline vehicles. Light-off temperature was defined as the time required to achieve 50% of maximum conversion efficiency. Vehicles were tested on a chassis dynamometer over the EPA driving cycle starting from cold ambient conditions (22°C).",
        "Results": "Formulation X achieved light-off in 45 seconds. Formulation Y achieved light-off in 62 seconds. Formulation Z achieved light-off in 38 seconds. All formulations underperformed relative to the manufacturer's baseline, which achieves light-off in 25 seconds. Formulation Z showed the fastest light-off but degraded fastest after 5,000 miles.",
        "Discussion": "The claimed 38-second light-off for Formulation Z is notably faster than the 62-second and 45-second results for Formulations Y and X, respectively. However, the rapid degradation after 5,000 miles raises concerns about long-term durability. The 25-second manufacturer baseline suggests that current aftermarket formulations still have significant room for improvement. Our results indicate that Formulation Z's apparent advantage may be short-lived.",
        "Conclusion": "While Formulation Z offers the fastest initial light-off among aftermarket options, durability concerns and poor performance relative to manufacturer baselines limit its practical value. Future research should focus on stable formulations that can consistently achieve light-off below 40 seconds without rapid degradation.",
    },
)

# Paper 5: Theoretical synthesis paper
paper5 = Paper(
    id="paper5",
    title="A Unified Framework for Contradiction Detection in Scientific Literature",
    authors=["Prof. Michael Anderson", "Dr. Lisa Wang"],
    abstract="We present a comprehensive framework for detecting contradictions across scientific papers. Our approach combines semantic similarity analysis with methodology context mapping to identify empirical, methodological, and theoretical contradictions.",
    full_text="""A Unified Framework for Contradiction Detection in Scientific Literature

The automated detection of contradictions across the scientific literature is an emerging challenge. With thousands of papers published annually, manual review is infeasible. We present a comprehensive framework for detecting contradictions across scientific papers. Our approach combines semantic similarity analysis with methodology context mapping to identify empirical, methodological, and theoretical contradictions.

METHODS: We curated a benchmark dataset of 500 paper pairs with annotated contradictions. Each claim was normalized and represented using BERT embeddings. Methodology context was extracted using dependency parsing and named entity recognition. We evaluated three contradiction types: empirical (conflicting results), methodological (conflicting procedures), and theoretical (conflicting assumptions or axioms).

RESULTS: Our system achieved an F1 score of 0.76 on the empirical contradiction task, 0.69 on methodological contradictions, and 0.62 on theoretical contradictions. The semantic similarity component contributed 45% of the empirical F1 score. Methodology context mapping improved methodological contradiction detection by 31% over baseline models.

DISCUSSION: The varying performance across contradiction types highlights the importance of domain-specific context. Empirical contradictions are more readily detectable through result comparison, while methodological and theoretical contradictions require deeper analysis of experimental design and foundational assumptions. Our framework provides a foundation for automated literature review systems.

CONCLUSION: Automated contradiction detection is feasible but performance varies by contradiction type. Empirical contradictions are best detected through direct result comparison, while methodological and theoretical contradictions require sophisticated context analysis. This work enables scalable literature analysis for identifying scientific consensus and conflict.

All code and benchmark datasets are publicly available for replication.""",
    sections={
        "Abstract": "We present a comprehensive framework for detecting contradictions across scientific papers. Our approach combines semantic similarity analysis with methodology context mapping to identify empirical, methodological, and theoretical contradictions.",
        "Methods": "We curated a benchmark dataset of 500 paper pairs with annotated contradictions. Each claim was normalized and represented using BERT embeddings. Methodology context was extracted using dependency parsing and named entity recognition. We evaluated three contradiction types: empirical (conflicting results), methodological (conflicting procedures), and theoretical (conflicting assumptions or axioms).",
        "Results": "Our system achieved an F1 score of 0.76 on the empirical contradiction task, 0.69 on methodological contradictions, and 0.62 on theoretical contradictions. The semantic similarity component contributed 45% of the empirical F1 score. Methodology context mapping improved methodological contradiction detection by 31% over baseline models.",
        "Discussion": "The varying performance across contradiction types highlights the importance of domain-specific context. Empirical contradictions are more readily detectable through result comparison, while methodological and theoretical contradictions require deeper analysis of experimental design and foundational assumptions. Our framework provides a foundation for automated literature review systems.",
        "Conclusion": "Automated contradiction detection is feasible but performance varies by contradiction type. Empirical contradictions are best detected through direct result comparison, while methodological and theoretical contradictions require sophisticated context analysis. This work enables scalable literature analysis for identifying scientific consensus and conflict.",
    },
)

# ============================================================
# Ground-Truth Dataset with 5 Evaluation Pairs
# ============================================================

# Define the ground-truth contradictions as dicts (for JSON serialization)
# Pair 1: Empirical contradiction - Drug X efficacy difference between 12-week and 6-week studies
gt_contradiction_1 = {
    "id": "con-001",
    "claim_a_id": "paper1-claim-0",
    "claim_a_quote": "At week 12, the Drug X group showed a mean systolic blood pressure reduction of 28.5 mmHg (SD 8.2)",
    "claim_b_id": "paper2-claim-0",
    "claim_b_quote": "At week 6, the Drug X group showed a mean systolic blood pressure reduction of 8.7 mmHg (SD 5.3)",
    "contradiction_type": "empirical",
    "confidence_score": 0.92,
    "explanation": "The 12-week Drug X trial showed statistically significant blood pressure reduction (p < 0.001) while the 6-week trial did not reach significance (p = 0.12), representing a contradictory empirical finding.",
    "evidence_level": "high",
}

# Pair 2: Methodological contradiction - Catalyst temperature optima differences
gt_contradiction_2 = {
    "id": "con-002",
    "claim_a_id": "paper3-claim-0",
    "claim_a_quote": "Converter A achieved peak efficiency (92% CO reduction) at 600°C",
    "claim_b_id": "paper4-claim-0",
    "claim_b_quote": "Formulation Z achieved light-off in 38 seconds",
    "contradiction_type": "methodological",
    "confidence_score": 0.78,
    "explanation": "These claims involve different methodological approaches to evaluating catalyst/converter performance - one measuring efficiency at specific temperatures, the other measuring light-off time. The methodologies differ fundamentally in what is being measured and how.",
    "evidence_level": "medium",
}

# Pair 3: Empirical contradiction - Catalyst efficiency claims
gt_contradiction_3 = {
    "id": "con-003",
    "claim_a_id": "paper3-claim-1",
    "claim_a_quote": "Below 400°C, all converters showed efficiency drops below 70%",
    "claim_b_id": "paper4-claim-1",
    "claim_b_quote": "Formulation Z maintained 50% efficiency for 5,000 miles, after which conversion efficiency dropped below 70%",
    "contradiction_type": "empirical",
    "confidence_score": 0.85,
    "explanation": "Paper 3 claims efficiency drops below 70% below 400°C across all converters, while Paper 4 reports Formulation Z maintained 50% efficiency (which is below the 70% threshold) for 5,000 miles. Both claims reference the 70% efficiency threshold but from different contexts and time/temperature domains.",
    "evidence_level": "high",
}

# Pair 4: Theoretical contradiction - Framework approaches
gt_contradiction_4 = {
    "id": "con-004",
    "claim_a_id": "paper5-claim-0",
    "claim_a_quote": "Our system achieved an F1 score of 0.76 on the empirical contradiction task",
    "claim_b_id": "paper1-claim-1",
    "claim_b_quote": "Approximately 65% of Drug X patients achieved target blood pressure (<140/90 mmHg) compared to 35% in the placebo group",
    "contradiction_type": "theoretical",
    "confidence_score": 0.65,
    "explanation": "These claims represent different theoretical approaches to evaluating treatment efficacy - one presents machine learning system performance (F1 score), the other presents clinical trial response rates. The methodologies and metrics are fundamentally different, representing different theoretical frameworks for evaluation.",
    "evidence_level": "low",
}

# Pair 5: Methodological contradiction - Light-off vs efficiency measurement
gt_contradiction_5 = {
    "id": "con-005",
    "claim_a_id": "paper3-claim-2",
    "claim_a_quote": "Converter A achieved peak efficiency (92% CO reduction) at 600°C",
    "claim_b_id": "paper4-claim-2",
    "claim_b_quote": "Formulation X achieved light-off in 45 seconds",
    "contradiction_type": "methodological",
    "confidence_score": 0.72,
    "explanation": "These claims use different methodological metrics - catalytic converter efficiency (percentage reduction at specific temperature) versus catalyst light-off time (seconds to 50% efficiency). The different metrics and measurement protocols represent a methodological contradiction in evaluation approach.",
    "evidence_level": "medium",
}

# Build the complete ground-truth dataset as plain dicts
ground_truth_dataset = {
    "dataset_name": "Lit-Contradict Sample Benchmark v2.0",
    "total_paper_pairs": 5,
    "paper_order": ["paper1", "paper2", "paper3", "paper4", "paper5"],
    "paper_descriptions": {
        "paper1": "12-week Drug X hypertension trial",
        "paper2": "6-week Drug X mild hypertension study",
        "paper3": "Catalytic converter temperature efficiency study",
        "paper4": "Aftermarket catalyst light-off performance study",
        "paper5": "Automated contradiction detection framework paper",
    },
    "paper_pairs": [
        ["paper1", "paper2"],  # Pair 1: Empirical
        ["paper3", "paper4"],  # Pair 2: Methodological
        ["paper3", "paper5"],  # Pair 3: Empirical (efficiency threshold)
        ["paper5", "paper1"],  # Pair 4: Theoretical (framework vs clinical)
        ["paper3", "paper4"],  # Pair 5: Methodological (efficiency vs light-off)
    ],
    "contradictions": [gt_contradiction_1, gt_contradiction_2, gt_contradiction_3, gt_contradiction_4, gt_contradiction_5],
}

if __name__ == "__main__":
    output_path = "ground_truth.json" if len(sys.argv) < 2 else sys.argv[1]
    with open(output_path, "w") as f:
        json.dump(ground_truth_dataset, f, indent=2)
    print(f"Ground-truth dataset written to {output_path}")

    # Also print paper summaries for verification
    print("\n--- Paper Summary ---")
    for p in [paper1, paper2, paper3, paper4, paper5]:
        print(f"\n{p.id}: {p.title}")
        print(f"  Abstract: {p.abstract[:80]}...")
        print(f"  full_text length: {len(p.full_text)} chars")
        print(f"  Sections: {list(p.sections.keys())}")