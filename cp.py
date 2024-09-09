from joblib import Parallel, delayed
import numpy as np

# Define your graph or tree structure
# For simplicity, let's represent the graph as an adjacency list
# This can be extended for more complex graph representations
graph = {
    0: [1, 2],
    1: [0, 3, 4],
    2: [0, 5, 6],
    3: [1],
    4: [1],
    5: [2],
    6: [2]
}

# Function for Breadth First Search (BFS)
def bfs(graph, start):
    visited = np.zeros(len(graph), dtype=bool)
    queue = [start]
    visited[start] = True

    while queue:
        node = queue.pop(0)
        print("Visiting node:", node)
        for neighbor in graph[node]:
            if not visited[neighbor]:
                queue.append(neighbor)
                visited[neighbor] = True

# Function for Depth First Search (DFS)
def dfs(graph, start, visited=None):
    if visited is None:
        visited = np.zeros(len(graph), dtype=bool)
    visited[start] = True
    print("Visiting node:", start)

    for neighbor in graph[start]:
        if not visited[neighbor]:
            dfs(graph, neighbor, visited)

# Example usage
start_node = 0
print("Parallel BFS:")
Parallel(n_jobs=-1)(delayed(bfs)(graph, start_node))

print("\nParallel DFS:")
Parallel(n_jobs=-1)(delayed(dfs)(graph, start_node))
