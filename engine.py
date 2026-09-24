import math
import numpy as np
import networkx as nx

def combine_impacts(existing, contribution):
    existing = float(np.clip(existing, 0, 100))
    contribution = float(np.clip(contribution, 0, 100))
    result = 100 * (1 - (1 - existing / 100) * (1 - contribution / 100))
    return float(np.clip(result, 0, 100))

def get_effective_weight(graph, u, v, memory):
    base = float(graph[u][v]["weight"])
    adaptive_multiplier = float(memory.get((u, v), 1.0))
    return float(np.clip(base * adaptive_multiplier, 0.0, 1.0))

def get_timeline_impacts(graph, shock_sources_dict, actions=None, memory=None, steps=4):
    if actions is None:
        actions = []
    if memory is None:
        memory = {}

    reductions = {(a["source"], a["target"]): float(a["reduction"]) for a in actions}
    current = {node: 0.0 for node in graph.nodes}

    for source, magnitude in shock_sources_dict.items():
        if source in current:
            current[source] = float(np.clip(magnitude, 0, 100))

    timeline = {"T0": current.copy()}

    for step in range(1, steps + 1):
        next_impacts = current.copy()
        for u, v in graph.edges():
            effective_weight = get_effective_weight(graph, u, v, memory)
            reduction = reductions.get((u, v), 0.0)
            effective_weight *= (1 - reduction / 100.0)
            effective_weight = float(np.clip(effective_weight, 0, 1))

            contribution = current[u] * effective_weight
            next_impacts[v] = combine_impacts(next_impacts[v], contribution)

        current = next_impacts
        timeline[f"T{step}"] = current.copy()

    return timeline

def final_impacts(timeline):
    return timeline[list(timeline.keys())[-1]]

def calculate_total_damage(impacts):
    return float(sum(max(0.0, x) for x in impacts.values()))

def calculate_containment(baseline_damage, final_damage):
    if baseline_damage <= 0:
        return 0.0
    value = ((baseline_damage - final_damage) / baseline_damage) * 100
    return float(np.clip(value, 0, 100))

def predictive_forecast(graph, shocks, memory, steps=4, simulations=250, uncertainty=0.12, seed=42):
    rng = np.random.default_rng(seed)
    node_values = {n: [] for n in graph.nodes}
    total_damage = []

    for _ in range(int(simulations)):
        sampled_memory = {}
        for u, v in graph.edges():
            base_mult = float(memory.get((u, v), 1.0))
            sampled_memory[(u, v)] = float(np.clip(
                rng.normal(base_mult, max(0.01, uncertainty * base_mult)),
                0.50, 1.50
            ))

        sampled_shocks = {
            n: float(np.clip(rng.normal(m, max(1.0, uncertainty * m)), 0, 100))
            for n, m in shocks.items()
        }
        tl = get_timeline_impacts(graph, sampled_shocks, actions=[], memory=sampled_memory, steps=steps)
        final = final_impacts(tl)
        for node in graph.nodes:
            node_values[node].append(float(final.get(node, 0.0)))
        total_damage.append(calculate_total_damage(final))

    rows = []
    for node, values in node_values.items():
        arr = np.asarray(values, dtype=float)
        rows.append({
            "Node": node,
            "Expected Impact (%)": float(arr.mean()),
            "P50 Impact (%)": float(np.percentile(arr, 50)),
            "P90 Impact (%)": float(np.percentile(arr, 90)),
            "P95 Impact (%)": float(np.percentile(arr, 95)),
        })
    forecast = pd.DataFrame(rows).sort_values("P90 Impact (%)", ascending=False).reset_index(drop=True)
    damage_arr = np.asarray(total_damage, dtype=float)
    summary = {
        "expected_damage": float(damage_arr.mean()),
        "p50_damage": float(np.percentile(damage_arr, 50)),
        "p90_damage": float(np.percentile(damage_arr, 90)),
        "p95_damage": float(np.percentile(damage_arr, 95)),
    }
    return forecast, summary
  
