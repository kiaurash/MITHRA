#!/usr/bin/env python3
"""
RLT Structure Validator for ARCHE
Checks: single root, no isolated nodes, proper edge pairing
"""

import pydot
from collections import defaultdict

def validate_rlt(dot_file):
    """Validate RLT structure according to ARCHE requirements"""

    issues = []

    # Parse DOT file
    try:
        graphs = pydot.graph_from_dot_file(dot_file)
        graph = graphs[0]
    except Exception as e:
        return [f"Failed to parse DOT file: {e}"]

    # Get all nodes and edges
    nodes = {node.get_name(): node for node in graph.get_nodes()}
    edges = graph.get_edges()

    # Track incoming and outgoing edges for each node
    incoming = defaultdict(list)
    outgoing = defaultdict(list)

    for edge in edges:
        src = edge.get_source()
        dst = edge.get_destination()
        label = edge.get_label() or ''
        label = label.strip('"')

        outgoing[src].append({'target': dst, 'label': label})
        incoming[dst].append({'source': src, 'label': label})

    # Check 1: Single root node (no outgoing edges)
    roots = [node for node in nodes if len(outgoing[node]) == 0]

    if len(roots) == 0:
        issues.append("ERROR: No root node found (all nodes have outgoing edges)")
    elif len(roots) > 1:
        issues.append(f"ERROR: Multiple root nodes found: {roots}")
    else:
        print(f"[OK] Single root node: {roots[0]}")

    # Check 2: No isolated nodes (all nodes connected to main graph)
    # We'll do BFS from root
    if len(roots) == 1:
        root = roots[0]
        visited = set()
        queue = [root]

        # BFS backwards (following incoming edges)
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            for edge_info in incoming[current]:
                source = edge_info['source']
                if source not in visited:
                    queue.append(source)

        isolated = set(nodes.keys()) - visited
        if isolated:
            issues.append(f"ERROR: Isolated nodes found: {isolated}")
        else:
            print(f"[OK] No isolated nodes (all {len(visited)} nodes connected to root)")

    # Check 3: Proper edge pairing
    valid_edge_types = {
        'deduction-rule', 'deduction-case',
        'abduction-phenomenon', 'abduction-knowledge',
        'induction-case', 'induction-common'
    }

    pairing_errors = []

    for node, edges_in in incoming.items():
        if len(edges_in) == 0:
            continue  # Leaf node

        # Get edge labels
        labels = [e['label'] for e in edges_in]

        # Check if all labels are valid
        for label in labels:
            if label not in valid_edge_types:
                pairing_errors.append(f"Node {node}: Invalid edge type '{label}'")

        # Check pairing rules
        label_set = set(labels)

        # Count each type
        deduction_rule_count = labels.count('deduction-rule')
        deduction_case_count = labels.count('deduction-case')
        abduction_phen_count = labels.count('abduction-phenomenon')
        abduction_know_count = labels.count('abduction-knowledge')
        induction_case_count = labels.count('induction-case')
        induction_common_count = labels.count('induction-common')

        # Check valid pairings
        has_deduction = deduction_rule_count > 0 or deduction_case_count > 0
        has_abduction = abduction_phen_count > 0 or abduction_know_count > 0
        has_induction = induction_case_count > 0 or induction_common_count > 0

        # Mixed paradigms check
        paradigm_count = sum([has_deduction, has_abduction, has_induction])
        if paradigm_count > 1:
            pairing_errors.append(f"Node {node}: Mixed reasoning paradigms (should use intermediate nodes)")

        # Deduction pairing
        if has_deduction:
            if deduction_rule_count != 1 or deduction_case_count < 1:
                pairing_errors.append(
                    f"Node {node}: Deduction requires exactly 1 'deduction-rule' and >=1 'deduction-case' "
                    f"(found {deduction_rule_count} rule, {deduction_case_count} case)"
                )

        # Abduction pairing
        if has_abduction:
            if abduction_phen_count != 1 or abduction_know_count != 1:
                pairing_errors.append(
                    f"Node {node}: Abduction requires exactly 1 'abduction-phenomenon' and 1 'abduction-knowledge' "
                    f"(found {abduction_phen_count} phenomenon, {abduction_know_count} knowledge)"
                )

        # Induction pairing
        if has_induction:
            if induction_common_count != 1 or induction_case_count < 1:
                pairing_errors.append(
                    f"Node {node}: Induction requires exactly 1 'induction-common' and >=1 'induction-case' "
                    f"(found {induction_common_count} common, {induction_case_count} case)"
                )

    if pairing_errors:
        issues.extend(pairing_errors)
    else:
        print(f"[OK] All edge pairings are valid")

    # Summary
    print(f"\n{'='*60}")
    if issues:
        print(f"[X] VALIDATION FAILED: {len(issues)} issues found")
        print(f"{'='*60}\n")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print(f"[OK] VALIDATION PASSED: RLT structure is valid")
        print(f"{'='*60}")
        print(f"Total nodes: {len(nodes)}")
        print(f"Total edges: {len(edges)}")
        print(f"Root node: {roots[0]}")

    return issues

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_rlt.py <dot_file>")
        sys.exit(1)

    dot_file = sys.argv[1]
    issues = validate_rlt(dot_file)

    sys.exit(0 if len(issues) == 0 else 1)
