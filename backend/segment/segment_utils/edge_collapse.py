import pymeshlab

def edge_collapse(mesh, e):
    """
    Collapses a mesh by collapsing its edges

    Inputs  
        :mesh: <pymeshlab> Mesh to be collapsed
    
    Outputs
        :returns: collapsed mesh with only e new edges
    """
    edge_count = mesh.edge_number()
    if edge_count < e: raise ValueError(f"Insufficient number of edges: [edge_count] >> {edge_count} < {e}")
    
    faces = mesh.face_matrix()
    vertics = mesh.vertex_matrix()
    edges = get_edges(faces, vertices)

    edge_feature_count = 5
    edge_features = get_edge_feature_map(edges)

    # while e > 0:
        

