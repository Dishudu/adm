import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.animation import PillowWriter
from matplotlib.animation import FFMpegWriter

def build_residual(G, flow):
    """
    По графу G и текущему потоку flow строим остаточную сеть R.
    R — ориентированный граф, где каждому ребру (u,v) соответствует
    два ребра:
      - прямое (u->v) с оставшейся capacity = G[u][v]['capacity'] - flow[(u,v)]
      - обратное (v->u) с capacity = flow[(u,v)]
    """
    R = nx.DiGraph()
    for u, v, data in G.edges(data=True):
        cap = data['capacity']
        f = flow[(u, v)]
        if cap - f > 0:
            R.add_edge(u, v, capacity=cap - f)
        if f > 0:
            R.add_edge(v, u, capacity=f)
    return R

def find_augmenting_path(R, s, t, path=None, visited=None):
    """
    Ищем любой увеличивающий путь из s в t в остаточной сети R.
    Возвращаем сам путь и bottleneck (min capacity).
    DFS-рекурсия.
    """
    if path is None:
        path = [s]
        visited = set([s])
    if s == t:
        bottleneck = min(R[path[i]][path[i+1]]['capacity'] for i in range(len(path)-1))
        return path, bottleneck
    for _, nbr, data in R.out_edges(s, data=True):
        if nbr not in visited and data['capacity'] > 0:
            visited.add(nbr)
            res = find_augmenting_path(R, nbr, t, path + [nbr], visited)
            if res is not None:
                return res
    return None

def apply_flow_update(R, flow, path, bottleneck):
    """
    Применяем найденный поток bottleneck к основному словарю flow
    и обновляем остаточную сеть R (в словаре flow остаётся правильная
    суммарная картина, но R здесь не используется далее, т.к. мы будем
    строить новую каждый раз).
    """
    for i in range(len(path)-1):
        u, v = path[i], path[i+1]
        if (u, v) in flow:
            flow[(u, v)] += bottleneck
        else:
            flow[(v, u)] -= bottleneck

def visualize_ford_fulkerson(G, source, sink):
    flow = { (u,v): 0 for u,v in G.edges() }
    stages = []

    while True:
        R = build_residual(G, flow)
        res = find_augmenting_path(R, source, sink)
        stages.append((R.copy(), [], flow.copy()))
        if res is None:
            break
        path, bottleneck = res
        stages.append((R.copy(), path[:], flow.copy()))
        apply_flow_update(R, flow, path, bottleneck)
        stages.append((R.copy(), path[:], flow.copy()))

    pos = nx.spring_layout(G)
    fig, ax = plt.subplots(figsize=(6, 4))

    def update(frame):
        ax.clear()
        R, P, F = stages[frame]
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='lightblue')
        path_edges = list(zip(P, P[1:])) if len(P) > 1 else []
        other_edges = [e for e in G.edges() if e not in path_edges]
        nx.draw_networkx_edges(G, pos, edgelist=other_edges, ax=ax)
        if path_edges:
            nx.draw_networkx_edges(G, pos, edgelist=path_edges,
                                   ax=ax, width=3, edge_color='red')
        labels = { (u,v): f"{F[(u,v)]}/{G[u][v]['capacity']}"
                   for u, v in G.edges() }
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, ax=ax)
        nx.draw_networkx_labels(G, pos, ax=ax)
        ax.set_title(f"Шаг {frame+1} / {len(stages)}")
        ax.axis('off')

    anim = FuncAnimation(fig, update, frames=len(stages), interval=100, repeat=False)

    #сохранить в GIF
    anim.save('ford_fulkerson1.gif', writer=PillowWriter(fps=0.5))

    #сохранить в MP4
    anim.save('ford_fulkerson1.mp4', writer=FFMpegWriter(fps=0.5, metadata=dict(artist='Me'), bitrate=1800))

    plt.show()

if __name__ == "__main__":
    G = nx.DiGraph()

    edges = [
    (0, 1, 10),
    (0, 2, 8),
    (1, 2, 2),
    (1, 3, 5),
    (2, 3, 10),
    (2, 4, 5),
    (3, 4, 7),
    ]
    for u, v, cap in edges:
        G.add_edge(u, v, capacity=cap)

    visualize_ford_fulkerson(G, source=0, sink=3)
