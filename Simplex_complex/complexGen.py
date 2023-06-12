from disjoint_set import DisjointSet
from gudhi.alpha_complex import AlphaComplex


def generate_alpha_complex(datapoints, filtration_value):
    simplexPoints = []
    local_to_global_id = {}

    for p in datapoints:
        simplexPoints.append((p.Lat, p.Long))
        local_to_global_id[len(simplexPoints) - 1] = p.Index

    ac = AlphaComplex(points=simplexPoints)
    stree = ac.create_simplex_tree()
    simps = []
    for filtered_value in stree.get_filtration():
        if filtered_value[1] <= filtration_value:
            simps.append(filtered_value)

    real_simps = []
    for s in range(len(simps)):
        simp = simps[s]
        simplex = simp[0]
        if len(simplex) == 1:
            real_simps.append(([local_to_global_id[simplex[0]]], simp[1]))
        if len(simp[0]) == 2:
            real_simps.append(([local_to_global_id[simplex[0]], local_to_global_id[simplex[1]]], simp[1]))
        if len(simp[0]) == 3:
            real_simps.append(([local_to_global_id[simplex[0]], local_to_global_id[simplex[1]],
                                local_to_global_id[simplex[2]]], simp[1]))

    return real_simps


def find_connected_components(simplicies):
    set = DisjointSet()
    for simp in simplicies:
        if len(simp[0]) == 2:
            set.union(simp[0][0], simp[0][1])

    groupReps = {}
    for simp in simplicies:
        if len(simp[0]) == 1:
            groupReps[simp[0][0]] = set.find(simp[0][0])

    return set, groupReps
