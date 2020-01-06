from collections import defaultdict
from queue import PriorityQueue

def dijkstra(edges:list, from_node:int, to_node:int):
    '''
    @param:
        edges: list of (from, to, cost) tuples
        from_node: from_node, int
        to_node: to_node, int

    @return:
        dist: shortest distance
        path: shortest path
    '''

    G = defaultdict(list)
    for f, t, c in edges:
        G[f].append((t, c))
        G[t].append((f, c))

    q = PriorityQueue()
    q.put((0, from_node, (from_node,)))

    dist = {from_node: 0}
    visited = set()

    while not q.empty():
        cost1, v1, path = q.get()

        # hit target
        if v1 == to_node:
            return cost1, path

        # check neighbours
        visited.add(v1)
        for v2, cost2 in G[v1]:
            # print(v1, v2, cost2)
            if v2 not in visited:
                old_cost = dist.get(v2, float("inf"))
                new_cost = cost1 + cost2
                # print(new_cost, old_cost)
                if new_cost < old_cost:
                    q.put((new_cost, v2, path + (v2,)))

    return float("inf"), []


if __name__ == "__main__":
    edges = [
        ('A', 'B', 6.5),
        ('A', 'F', 2.2),
        ('B', 'E', 3.2),
        ('B', 'D', 4.2),
        ('B', 'C', 1.1),
        ('C', 'D', 1.6),
        ('D', 'E', 2.9),
        ('D', 'F', 0.7),
        ('E', 'F', 6.2)
    ]

    import string
    for to_node in string.ascii_uppercase[1: 6]:
        d, p = dijkstra(edges, 'A', to_node)
        print(d, p)
