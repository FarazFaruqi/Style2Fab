import os
import re
import pathlib
import pymeshlab
import numpy as np
import scipy.sparse.linalg
from .mesh_graph import MeshGraph
from scipy.cluster.vq import kmeans2

### Global Constants ###
yes = {"yes", "yeah", "y", "yea"}

def segment_mesh(mesh, k, collapsed = True):
    """
    Segments a mesh as follows:
        1. Converts mesh into a face graph, where 
            - each node is a face 
            - faces have edges between them iff they are adjacent 
            - weights of the edge between fi and fj = w(fi, fj) = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist
                - ang_dist(fi, fj) = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180
                - geodisc(fi, fj) = distance from center of fi to center of fj
        2. Collapse mesh to be of lower dimension
            - each node is now a set of faces
            - nodes have edges between them iff both sets share at least one pair of adjacent faces
            - weights of the edge between ni and nj = w(ni, nj) = δ * (geodisc(ni, nj)) / avg_geodisc + (1 - δ) * (ang_dist(ni, nj)) / avg_ang_dist
                - ang_dist(ni, nj) = η * (1 - cos(α_avg(ni, nj))); η = 1 for α_avg >= 180 and η -> 0 for α_avg < 180
                - geodisc(ni, nj) = distance from center of ni to center of nj

        3. We compute similarity matrix M
            (How Katz and Tal did it) - Probabilistic approach 
            Decide on k faces (n1, n2, ..., nk) to be the 'centroid nodes' of the graph
            For each node we compute the probability that it belongs to class k 
                - P_j(fi) = [1/w(ni, nj)] / [1/w(ni, n1) + 1/w(ni, n2) + ... + 1/w(ni, nk)]

            (How Liu and Zhang did it) - Spectural Clustering approach
            For each pair of nodes (fi, fj) we compute the similarity as 
                - Sim(fi, fj) = e^(-w(ni, nj) / [2 * (avg_w) ** 2]) if w(ni, nj) != inf & fi != fj
                              = 0 if w(ni, nj) == inf
                              = 1 if ni == nj
        3. Compute normal Laplacian of M, L
            - L = sqrt(D).T * M.T * sqrt(D); D is degree matrix of the face graph
        4. We compute eigenvalues and vectors of L
        5. We preform K-means clustering (or other technique) on first k egienvectors
    """
    # Step 1
    mesh_graph = MeshGraph(mesh)

    # Step 2
    similarity_matrix = mesh_graph.similarity_matrix(collapsed = collapsed)

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.collapsed_degree_matrix) if collapsed else np.sqrt(mesh_graph.degree_matrix)
    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree

    # Step 4
    eigen_values, eigen_vectors = scipy.sparse.linalg.eigsh(laplacian) # Eigen values here can be used to get the value of k  = num < epsilon (0.5)
    eigen_vectors /= np.linalg.norm(eigen_vectors, axis=1)[:,None]

    # Step 5
    _, labels = kmeans2(eigen_vectors, k, minit="++", iter=100)

    if collapsed: labels = _unwrap_labels(mesh_graph, labels)
    print(f"\033[33m[Out] >> Segmented mesh into {len(set(labels))} segments\033[0m")
    return labels

def extract_segments(vertices, faces, labels, name = ""):
    """
    Extracts the segments of a mesh by saving a hash map from original mesh face -> segmented mesh face
    for reconstruction

    Inputs
        :vertices: <np.ndarray>
        :faces: <np.ndarray>
        :labels: <list<int>>
    """
    parent_dir = pathlib.Path(__file__).parent.resolve()
    i = len([name for name in os.listdir(f"{parent_dir}/models") if not os.path.isdir(name)])
    model_dir = f"{parent_dir}/models/model_{i}_{name}"
    _construct_dir(model_dir)
    
    segment_indices = {} 
    for j in range(len(labels)):
        label = labels[j]
        if label not in segment_indices: 
            _construct_dir(f"{model_dir}/segment_{label}")
            segment_indices[label] = []
        segment_indices[label].append(j)

    for label, indices in segment_indices.items():
        segment_faces = np.zeros((len(indices), 3))
        vertices_map = {}
        segment_vertices = []
    
        with open(f"{model_dir}/segment_{label}/face_indices.txt", "w+") as face_indices:
            face_indices.write("######## Face Indices Hash Map ########\nOriginal -> Segment\n\n")
            n = 0
            for j, k in enumerate(indices):
                face_indices.write(f"{j}\t->\t{k}\n")
                
                segment_face = []
                for v in faces[k]:
                    if v not in vertices_map: 
                        vertices_map[v] = n; n += 1
                        segment_vertices.append(vertices[v])
                    segment_face.append(vertices_map[v])

                segment_faces[j] = np.array(segment_face)
        
        ms = pymeshlab.MeshSet()
        mesh = pymeshlab.Mesh(np.array(segment_vertices), segment_faces)
        ms.add_mesh(mesh)
        ms.save_current_mesh(f"{model_dir}/segment_{label}/segment_{label}.obj")

### Helper Functions ####
def _remesh(mesh):
    """
    Resmeshes a mesh to force all faces to become polygons 

    Inputs
        :mesh: <pymeshlab.Mesh> mesh to be remeshed

    Throws
        <ValueError> if the number of verticies > number of vertex normals
    """
    ms = pymeshlab.MeshSet()
    ms.add_mesh(mesh)
    ms.meshing_isotropic_explicit_remeshing(iterations=3)

    return ms.current_mesh()

def _construct_dir(dir_name):
    """
    """
    os.mkdir(dir_name)

def _unwrap_labels(mesh_graph, labels):
    """
    Unwraps the collapsed labels back to cover the entire mesh

    Inputs  
        mesh_graph: <MeshGraph> a graph where every node is a set of faces and edges exist between adjacent set of faces
        labels: <np.ndarray> where the ith element is the label corresponding to the ith face set 
    
    Outputs 
        :returns: <list> where the ith element is the label corresponding to the ith face
    """
    n = len(mesh_graph.collapsed_map)
    
    unwrapped_labels = np.zeros(n)
    reverse_map = {}
    for i, j in mesh_graph.collapsed_map.items():
        try: reverse_map[j[1]].append(i)
        except: reverse_map[j[1]] = [i]

    for j, faces in reverse_map.items():
        for i in faces: unwrapped_labels[i] = labels[j]
    return unwrapped_labels

def batch_seg(meshes):
    """ 
    Segment a batch of meshes and stores each

    Inputs
        :meshes: <list<str, int>> absolute pathes of all meshes to segment 
                                  along with number of segments it should be segmented into
    """
    for mesh_path, k in meshes:
        collapsed = True
        ms = pymeshlab.MeshSet()
        ms.load_new_mesh(mesh_path)
        mesh = ms.current_mesh()

        faces = mesh.face_matrix()
        vertices = mesh.vertex_matrix()

        labels = segment_mesh(mesh, k, collapsed = collapsed)
        extract_segments(vertices, faces, labels)
    
# if __name__ == "__main__":
    # base_dir = "/home/ubuntu/fa3ds/backend/segment/segment_utils/models"
    # meshes = [
    #     (f"{base_dir}/vase.obj", 12)
    # ]
    # batch_seg(meshes)