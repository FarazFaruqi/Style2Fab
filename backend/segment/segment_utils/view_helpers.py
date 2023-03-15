import os
import re
import sys
import shutil
import pathlib
import pymeshlab
import traceback
import threading
import numpy as np
import pandas as pd
from time import time
import scipy.sparse.linalg
from .edge import edge_collapse
import matplotlib.pyplot as plt
from mesh_graph import MeshGraph
from scipy.cluster.vq import kmeans2
from sklearn.decomposition import PCA

### Global Constants ###
yes = {"yes", "yeah", "y", "yea"}
colors = [
    {"centroid": "red", "points": "red"},
    {"centroid": "green", "points": "green"},
    {"centroid": "black", "points": "black"},
    {"centroid": "yellow", "points": "yellow"},
    {"centroid": "blue", "points": "blue"},
    {"centroid": "orange", "points": "orange"},
    {"centroid": "purple", "points": "purple"},
    {"centroid": "pink", "points": "pink"},
    {"centroid": "violet", "points": "violet"},
    {"centroid": "brown", "points": "brown"},
    {"centroid": "gray", "points": "gray"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
    {"centroid": "red", "points": "blue"},
]
results_dir = "/home/ubuntu/fa3ds/backend/results"
default_models_dir = "/home/ubuntu/fa3ds/backend/results/auto_segmented_models"
report = lambda error: f"\033[31m----------------------------\n{error}\n----------------------------\033[0m\n"

def segment_mesh(mesh, k, face_count, collapsed = False, parallelize = False, extract = False, parent_dir = default_models_dir, mesh_dir = default_models_dir):
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
    print(f"--- Segmenting Mesh ---\nfaces: {mesh.face_matrix().shape}\nvertices: {mesh.vertex_matrix().shape}")
    start_time = time()
    # Step 0
    # mesh = edge_collapse(mesh, face_count = face_count)

    # Step 1
    mesh_graph = MeshGraph(mesh, collapsed = collapsed)

    # Step 2
    similarity_matrix = mesh_graph.similarity_matrix(collapsed = collapsed)

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.collapsed_degree_matrix) if collapsed else np.sqrt(mesh_graph.degree_matrix)
    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree

    if k is None:
        eigen_values_full, _ = scipy.linalg.eigh(laplacian) 
        eigen_values_full = np.sort(eigen_values_full)
        eigen_std = np.std(eigen_values_full)
        k = len([abs(eigen_values_full[i] - eigen_values_full[i - 1]) for i in range(1, len(eigen_values_full)) if abs(eigen_values_full[i] - eigen_values_full[i - 1]) >= eigen_std])
        print(f"\033[32mRecommended segment count for {mesh.face_matrix().shape} resolution: {k}\033[0m")
    print(f"Segmenting mesh into {k} segments")
    
    # Step 4
    eigen_values, eigen_vectors = scipy.sparse.linalg.eigsh(laplacian) # Eigen values here can be used to get the value of k  = num < epsilon (0.5)
    eigen_vectors /= np.linalg.norm(eigen_vectors, axis=1)[:,None]

    # Step 5
    labels = []
    faces = mesh.face_matrix()
    vertices = mesh.vertex_matrix()

    if parallelize:
        print(f"Should be segmented into {k} segments")
        def f(args):
            vertices, faces, mesh_graph, collapsed, k, t, eigen_vectors, extract, component_dir, mesh_dir = args

            _, labels = kmeans2(eigen_vectors, k, minit="++", iter=50) # changed k => number_of_segments for automatic segmentation
            if collapsed: labels = _unwrap_labels(mesh_graph, labels)
            if extract: extract_segments(vertices, faces, labels, k, t, component_dir, mesh_dir)
        
        new_thread = thread(i, f, [vertices, faces, mesh_graph, collapsed, k, time() - start_time, eigen_vectors, extract, parent_dir, mesh_dir])
        new_thread.start()
    else:
        _, labels = kmeans2(eigen_vectors, k, minit="++", iter=50)
        visualize_eigen_vectors(eigen_vectors, k, reduced = True)

        if collapsed: labels = _unwrap_labels(mesh_graph, labels)
        if extract: extract_segments(vertices, faces, labels, k, time() - start_time, parent_dir, mesh_dir)

    print(f"\033[33m[Out] >> Segmented mesh into {len(set(labels))} segments\033[0m")
    print(f"--- Done ---")
    return k, labels

def extract_segments(vertices, faces, labels, num_segments, t, parent_dir = default_models_dir, mesh_dir = default_models_dir):
    """
    Extracts the segments of a mesh by saving a hash map from original mesh face -> segmented mesh face
    for reconstruction

    Inputs
        :vertices: <np.ndarray>
        :faces: <np.ndarray>
        :labels: <list<int>>
    """
    # parent_dir = pathlib.Path(__file__).parent.resolve()
    # segmentation_dir = f"{parent_dir}/{num_segments}_segmentation"
    # _construct_dir(segmentation_dir)
    segmentation_dir = parent_dir
    
    segment_indices = {} 
    for j in range(len(labels)):
        label = labels[j]
        if label not in segment_indices: 
            _construct_dir(f"{segmentation_dir}/segment_{label}")
            segment_indices[label] = []
        segment_indices[label].append(j)

    for label, indices in segment_indices.items():
        segment_faces = np.zeros((len(indices), 3))
        vertices_map = {}
        segment_vertices = []
    
        with open(f"{segmentation_dir}/segment_{label}/face_indices.txt", "w+") as face_indices:
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
        ms.save_current_mesh(f"{segmentation_dir}/segment_{label}/segment_{label}.obj")

    print(f"\033[33mSaving info to {segmentation_dir}/info.csv\033[0m")
    df = pd.DataFrame([[f"{segmentation_dir}/segment_{label}", faces.shape[0], num_segments, t]], columns=["meshPath", "resolution", "numSegments", "segmentationTime"])
    df.to_csv(f"{mesh_dir}/info.csv", mode='a', encoding='utf-8', index=False)

def visualize_eigen_vectors(eigen_vectors, k, n = 2, reduced = True):
    """
    Visualizes a set of eigen vectors (with reduced dimensionality to 2 or 3) 
    """
    pca_reducer = PCA(n, svd_solver='full')
    reduced_eigen_vectors = pca_reducer.fit_transform(eigen_vectors)
    reduced_eigen_vectors_sep = [
        reduced_eigen_vectors.T[i, :] 
        for i in range(n)
    ]
    centroids, labels = kmeans2(reduced_eigen_vectors, k, minit="++", iter=50)

    if n == 2:
        x, y = reduced_eigen_vectors_sep
        for i in range(k):
            plt.scatter(centroids[i][0], centroids[i][1], color=colors[i]['centroid'])

            plt.scatter(
                [x[j] for j in range(len(x)) if labels[j] == i],
                [y[j] for j in range(len(y)) if labels[j] == i],
                color=colors[i]['points']
            )
    else: 
        print(f"Support not yet added for visualizing {n}-D reduced eigen vectors")
        return

    # if os.path.exists(f"{results_dir}/eigenvectors.png"): os.remove(f"{results_dir}/eigenvectors.png")
    plt.savefig(f"{results_dir}/eigenvectors.png")

### Helper Classes ###
class thread(threading.Thread):
    def __init__(self, thread_id, f, args):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.args = args
        self.f = f
 
        # helper function to execute the threads
    def run(self):
        print(f"[{self.thread_id}] Starting ...")
        return self.f(self.args)
   
### Helper Functions ####
def _predict_segmentation(mesh, face_count, collapsed = False):
    """
    """
    mesh = edge_collapse(mesh, face_count = face_count)
    # Step 1
    mesh_graph = MeshGraph(mesh, collapsed)

    # Step 2
    similarity_matrix = mesh_graph.similarity_matrix(collapsed = collapsed)

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.collapsed_degree_matrix) if collapsed else np.sqrt(mesh_graph.degree_matrix)

    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree
    eigen_values_full, _ = scipy.linalg.eigh(laplacian) 
    eigen_values_full = np.sort(eigen_values_full)
    eigen_std = np.std(eigen_values_full)
    num_segments = len([abs(eigen_values_full[i] - eigen_values_full[i - 1]) for i in range(1, len(eigen_values_full)) if abs(eigen_values_full[i] - eigen_values_full[i - 1]) >= eigen_std])

    print(f"\033[32mRecommended segment count for {face_count} resolution: {num_segments}\033[0m")

    return mesh, num_segments
    
def _remesh(mesh, save_path = None):
    """
    Resmeshes a mesh to force all faces to become polygons 

    Inputs
        :mesh: <pymeshlab.Mesh> mesh to be remeshed

    Throws
        <ValueError> if the number of verticies > number of vertex normals
    """
    ms = pymeshlab.MeshSet()
    if isinstance(mesh, str): ms.load_new_mesh(mesh)
    else: ms.add_mesh(mesh)
    # ms.meshing_isotropic_explicit_remeshing(iterations=3)
    # ms.meshing_isotropic_explicit_remeshing(iterations=3, targetlen=pymeshlab.Percentage(1.5))

    ms.compute_matrix_from_scaling_or_normalization(scalecenter='origin', unitflag=True, uniformflag=True)
    targetlen_given = 1.5
    while True: 
        ms.meshing_isotropic_explicit_remeshing(iterations=4, targetlen=pymeshlab.Percentage(targetlen_given))
        if(ms.current_mesh().face_matrix().shape[0] < 24000):
            print(f"[remesh] >> Optimizing resolution {ms.current_mesh().face_matrix().shape[0]}...")
            targetlen_given -= 0.1
        elif(ms.current_mesh().face_matrix().shape[0] > 26000):
            print(f"[remesh] >> Optimizing resolution {ms.current_mesh().face_matrix().shape[0]}...")
            targetlen_given += 0.1
        else:
            print(f"[remesh] >> Optimization completed. Current resolution: {ms.current_mesh().face_matrix().shape[0]}... ")
            break

    ms.add_mesh(mesh)

    for i in ms: pass
    if save_path is not None: ms.save_current_mesh(save_path)
    return ms.current_mesh()

def _construct_dir(dir_name, overwrite = "y"):
    """
    Constructs a new directory with name dir_name, if one does not exist
    else it promopts user to over-write

    Inputs
        :dir_name: 
    """
    if os.path.exists(dir_name):
        if overwrite is None: overwrite = input(f"Directory {dir_name} exists, do you wish to overwrite [y, (n)]? ")
        if overwrite.lower() in yes: 
            shutil.rmtree(dir_name)
            os.mkdir(dir_name)
    else: os.mkdir(dir_name)

def _remove_dir(dir_name):
    """
    Removes a directory and its contained items

    Inputs
        :dir_name: 
    """
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

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
    for mesh_dir, (res, model_name) in meshes:
        mesh_save_dir = f"{default_models_dir}/{model_name}"
        _construct_dir(mesh_save_dir)
        print("Starting to loop over models...")
        ms = pymeshlab.MeshSet()

        for _, dirs, files in os.walk(mesh_dir):
            for i, file in enumerate(files):
                mesh_name, mesh_ext = os.path.splitext(file) 
                print(f"Testing {mesh_name}{mesh_ext} ...")
                if mesh_ext.lower() != ".obj": continue

                mesh_path = f"{mesh_dir}/{file}"
                component_dir = f"{mesh_save_dir}/component_{i}_{mesh_name.lower()}"
                _construct_dir(component_dir)
    
                collapsed = True

                # faces = mesh.face_matrix()
                # vertices = mesh.vertex_matrix()
                
                try: 
                    # def f(args):
                    #     mesh, K, face_count, collapsed, parent_dir = args 
                    
                    mesh = _remesh(mesh_path, save_path = f"{component_dir}/{mesh_name.lower()}.obj")
                    # for j, res in enumerate(resolutions):
                        # new_thread = thread(i, f, [mesh, K, resolution, collapsed, component_dir])
                        # new_thread.start()
                        # res_dir = f"{component_dir}/res_{res}" # For component based segmentation
                    # res_dir = f"{component_dir}" # For single model segmentation
                    # _construct_dir(res_dir)
                    segment_mesh(mesh, None, res, collapsed = collapsed, parallelize = False, etract = True, parent_dir = component_dir, mesh_dir = component_dir)

                    with open("/home/ubuntu/fa3ds/backend/segment/segment_utils/auto_segmented.txt", "a") as segmented:
                        segmented.write(f"{component_dir}\n") 
                            
                except Exception as error:
                    with open("/home/ubuntu/fa3ds/backend/segment/segment_utils/auto_skipped.txt", "a") as skipped:
                        skipped.write(f"model_{component_dir.split('_')[-1]}\n")
                    if "info.csv" not in os.listdir(component_dir): _remove_dir(component_dir)
                    print(report(f"{traceback.format_exc()}\nSegmentation failed :("))

                    continue
        if len(os.listdir(mesh_save_dir)) == 0:
            _remove_dir(mesh_save_dir)
   
if __name__ == "__main__":
    mesh_base_dir = "/home/ubuntu/scraped_models/formative_models"

    meshes = [["/home/ubuntu/scraped_models/formative_models", (25000, "formative_models")]]

    # for _, mesh_dirs, files in os.walk(mesh_base_dir):
    #     for mesh_dir in mesh_dirs:
    #         mesh_name, mesh_ext = os.path.splitext(mesh_dir)
    #         meshes.append([f"{mesh_base_dir}/{mesh_dir}", ([15000, 20000, 25000, 30000], mesh_name)])
    #     break

    batch_seg(meshes)
