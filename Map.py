import networkx as nx
import osmnx as ox


class Distance:

    def __init__(self, Adress, Distance):
        self.Adress = Adress
        self.To = None
        self.Distance = Distance
        self.From = None

    def setTo(self, To):
        self.To = To

    def setFrom(self, From):
        self.From = From

    def distance(self):
        if 'graph' not in self.__dict__:
            graph = ox.graph_from_address(self.Adress, dist=1000*self.Distance,
                                          network_type='drive', simplify=True)
            print("Mapa gerado com sucesso.")
            self.__dict__['graph'] = graph
        else:
            graph = self.__dict__['graph']
        orig_node = ox.nearest_nodes(graph, X=self.From['X'], Y=self.From['Y'])
        target_node = ox.nearest_nodes(graph, X=self.To['X'], Y=self.To['Y'])
        route = ox.shortest_path(graph, orig_node, target_node, weight="lenght")
        edge_lengths = ox.utils_graph.get_route_edge_attributes(graph, route, "length")
        return round(sum(edge_lengths)) / 1000
