import pymeshlab

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
    
def edge_collapse(mesh, face_count):
    """
    Collapses a mesh by collapsing its edges

    Inputs  
        :mesh: <pymeshlab> Mesh to be collapsed
    
    Outputs
        :returns: collapsed mesh with only e new edges
    """
    print(f"[faces] >> {mesh.face_matrix().shape}")
    print(f"[verts] >> {mesh.vertex_matrix().shape}")

    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=face_count)
    for i in ms: pass
    mesh = ms.current_mesh()
    
    faces = mesh.face_matrix()
    vertices = mesh.vertex_matrix()

    print(f"[collapsed faces] >> {faces.shape}")
    print(f"[collapsed verts] >> {vertices.shape}")

    return mesh

# if __name__ == "__main__":
#     mesh_path = "/home/ubuntu/fa3ds/backend/segment/segment_utils/ui_models/vase.obj"
#     ms = pymeshlab.MeshSet()
#     ms.load_new_mesh(mesh_path)
#     mesh = ms.current_mesh()
#     edge_collapse(mesh, 0.5)

