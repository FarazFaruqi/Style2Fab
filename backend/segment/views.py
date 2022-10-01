"""
segment views
"""
import os
import pymeshlab
import numpy as np
import scipy.sparse.linalg
from rest_framework import status
from django.shortcuts import render
from scipy.cluster.vq import kmeans2
from utils.view_helpers import _is_subset
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .segment_utils.mesh_graph import MeshGraph

@api_view(['POST'])
def segment(request, *args, **kwargs):
    """
    Segments provided mesh

    Inputs
        :request: <Response.HTTP> a requesting including the mesh specifying the vertices and the faces clusters to seperate mesh into, if None then number  | wbnnnis determined by finding the largest set of eigenvalues 
                         which are within ε away from each other, (default is None)
    
    Outputs
        :returns: <np.ndarray> Labels of size m x 1; m = len(mesh.vertex_matrix) where Labels[i] = label of vertex i ∈ [1, k]
    """
    data = {}
    segment_fields = ["vertices", "faces", "k", "collapsed"]
    segment_status   = _is_subset(segment_fields, request.keys())
    
    if segment_status == status.HTTP_200_OK:
        # Step 0 (Initialization of variables)
        k = request.data['k']
        collapsed = request.data['collapsed']
        faces = np.array(request.data['faces'])
        vertices = np.array(request.data['vertices'])
        
        mesh = pymeshlab.Mesh(vertices, faces)
        labels = segment(mesh, k, collapsed = collapsed)

        data['face_segments'] = labels
        data['labels'] = ["function", "function", "form", "function", "function", "form", "function", "form", "form", "function", "form", "function"]

    return Response(data = data, status = segment_status)

def segment(mesh, k, collapsed = True):
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
    similarity_matrix = mesh_graph.similarity_matrix()

    # Step 3
    sqrt_degree = np.sqrt(mesh_graph.collapsed_degree_matrix) if collapsed else np.sqrt(mesh_graph.degree_matrix)
    laplacian = sqrt_degree.T * similarity_matrix.T * sqrt_degree

    # Step 4
    eigen_values, eigen_vectors = scipy.sparse.linalg.eigsh(laplacian) # Eigen values here can be used to get the value of k  = num < epsilon (0.5)
    eigen_vectors /= np.linalg.norm(eigen_vectors, axis=1)[:,None]

    # Step 5
    _, labels = kmeans2(eigen_vectors, k, minit="++", iter=50)

    if collapsed: labels = _unwrap_labels(mesh_graph, labels)
    print(f"\033[33m[Out] >> Segmented mesh into {len(set(labels))} segments\033[0m")
    return labels

### Helper Functions ####
def _unwrap_labels(mesh_graph, labels):
    """
    Unwraps the collapsed labels back to cover the entire mesh

    Inputs  
        mesh_graph: <MeshGraph> a graph where every node is a set of faces and edges exist between adjacent set of faces
        labels: <np.ndarray> where the ith element is the label corresponding to the ith face set 
    
    Outputs 
        :returns: <list> where the ith element is the label corresponding to the ith face
    """
    n = mesh_graph.collapsed_map.shape[0]
    
    unwrapped_labels = np.zeros(n)
    reverse_map = {}
    for i, j in mesh_graph.collapsed_map.items():
        try: reverse_map[j[1]].append(i)
        except: reverse_map[j[1]] = [i]

    for j, faces in reverse_map.items():
        for i in faces: unwrapped_labels[i] = labels[j]
    return unwrapped_labels