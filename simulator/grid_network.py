import networkx as nx


def create_grid():

    G = nx.Graph()

    # main plant connections
    G.add_edge("Plant", "A", capacity=500)
    G.add_edge("Plant", "B", capacity=500)
    G.add_edge("Plant", "C", capacity=500)

    # area connections
    G.add_edge("A", "Area1", capacity=300)
    G.add_edge("B", "Area2", capacity=300)
    G.add_edge("C", "Area3", capacity=300)

    # cross-area connections
    G.add_edge("Area1", "Area2", capacity=200)
    G.add_edge("Area2", "Area3", capacity=200)
    G.add_edge("Area1", "Area3", capacity=200)

    return G


def route_power(grid, source, target, power):

    try:
        path = nx.shortest_path(grid, source=source, target=target)

        return path

    except nx.NetworkXNoPath:

        print("No route available")

        return None