#include <iostream>
#include <vector>
#include <algorithm>
#include <climits>

struct Edge {
    int to, cap, flow, rev;
    Edge(int v, int c, int f, int r) : to(v), cap(c), flow(f), rev(r) {}
};

std::vector<std::vector<Edge>> graph;

void addEdge(int u, int v, int cap) {
    graph[u].emplace_back(v, cap, 0, graph[v].size());
    graph[v].emplace_back(u, 0, 0, graph[u].size() - 1);
}

int dfs(int u, int t, std::vector<bool> &visited, int flow) {
    if (u == t) return flow;
    visited[u] = true;
    for (Edge &e : graph[u]) {
        int v = e.to;
        if (!visited[v] && e.flow < e.cap) {
            int cur_flow = std::min(flow, e.cap - e.flow);
            int temp_flow = dfs(v, t, visited, cur_flow);
            if (temp_flow > 0) {
                e.flow += temp_flow;
                graph[v][e.rev].flow -= temp_flow;
                return temp_flow;
            }
        }
    }
    return 0;
}

int fordFulkerson(int s, int t) {
    int max_flow = 0;
    while (true) {
        std::vector<bool> visited(graph.size(), false);
        int pushed = dfs(s, t, visited, INT_MAX);
        if (pushed == 0) break;
        max_flow += pushed;
    }
    return max_flow;
}

int main() {
    int n = 6;
    graph.assign(n, std::vector<Edge>());

    addEdge(0, 1, 16);
    addEdge(0, 2, 13);
    addEdge(1, 2, 10);
    addEdge(1, 3, 12);
    addEdge(2, 1, 4);
    addEdge(2, 4, 14);
    addEdge(3, 2, 9);
    addEdge(3, 5, 20);
    addEdge(4, 3, 7);
    addEdge(4, 5, 4);

    int source = 0, sink = 5;
    std::cout << "Max Flow: " << fordFulkerson(source, sink) << std::endl;
    return 0;
}
