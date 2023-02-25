class Edge():
    """ A simple edge where two edges are equal if they are equivalent sets """
    def __init__(self, v1, v2) -> None:
        self.v1 = v1
        self.v2 = v2
    
    def mean(self, vertices): 
        return (vertices[self.v1] + vertices[self.v2]) / 2

    def __iter__(self):
        for i in [self.v1, self.v2]: yield i
        
    def __eq__(self, __o: object) -> bool:
        return (self.v1 == __o.v1 and self.v2 == __o.v2) or (self.v1 == __o.v2 and self.v2 == __o.v1)
    
    def __hash__(self) -> int:
        return hash(self.v1) + hash(self.v2)

    def __str__(self) -> str:
        return f"{self.v1} ---- {self.v2}"

def get_edges(mesh):
    """
    Extracts the edges from a mesh

    Inputs
        :mesh: <pymeshlab.Mesh> Mesh to extract edges of 
    
    Outptus
        :np.array: of edges
    """
    edges = np.zeros((mesh.edge_number()))
    faces = mesh.face_matrix()

    i = 0
    for face in faces:
        v1, v2, v3 = face
        edge_1 = Edge(v1, v2)
        edge_2 = Edge(v2, v3)
        edge_3 = Edge(v1, v3)

        for edge in (edge_1, edge_2, edge_3):
            if edge not in edges:
                edges[i] = edge
                i += 1
    
    return edges
    


