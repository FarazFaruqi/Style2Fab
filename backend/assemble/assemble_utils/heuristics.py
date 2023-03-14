import pymeshlab

### Global Constants ###
heuristics = {
    "connectedness": connectedness
}

def check_heuristics(mesh_set):
    """
    Evaluates a set of heuristics on a set of meshes

    Inputs
        :mesh_set: <pymeshlab.MeshSet> of meshes which comprimise a subset of a model's 
                    power set

    Outputs
        :return: True if all heuristics pass, False otherwise 
    """
    for name, heuristic in heuristics.items():
        if not heuristic(mesh_set): 
            print(f"\033[31m[{name}] Failed!\033[39m")
            return False
        print(f"\033[32m[{name}] Passed!\033[39m")
    return True

### Heuristic ###
def connectedness(mesh_set):
    """
    Determines if a mesh set contains only connected meshes

    Inputs
        :mesh_set: <pymeshlab.MeshSet> of meshes which comprimise a subset of a model's 
                    power set

    Outputs
        :returns: True if all meshes in the mesh set are connected in 
                  3D euclidean space, False otherwise
    """
    faces = []
    vert_map = {}
    vertices = []
    f_color_matrix = []

    for i, mesh in enumerate(mesh_set):
        vertex_matrix = mesh.vertex_matrix()
        for j, face in enumerate(mesh.face_matrix()):
            for k, v in enumerate(face):
                if tuple(vertex_matrix[v]) not in vert_map: 
                    vert_map[tuple(vertex_matrix[v])] = len(vert_map)
                    vertices.append(vertex_matrix[v])
                face[k] = vert_map[tuple(vertex_matrix[v])]             
            faces.append(face)
            f_color_matrix.append(colors[i][1])
    
    faces = np.array(faces)
    vertices = np.array(vertices)

    ### Construct graph and check if it is connected or not (preform bfs)

    return True