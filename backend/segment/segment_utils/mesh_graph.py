
import sys
import scipy
import pymeshlab
import numpy as np
from time import time
from tqdm import tqdm
from edge import Edge
from face import Face
sys.setrecursionlimit(10000)

### Global Constants ###
_coords = lambda vertices, indicies: np.array([vertices[i] for i in indicies])

class MeshGraph():
    """
    AF(mesh) = Converts mesh into a collapsed mesh graph, where 
                - each node is now a set of faces
                - nodes have edges between them iff both sets share at least one pair of adjacent faces
                - weights of the edge between ni and nj = w(ni, nj) = δ * (geodisc(ni, nj)) / avg_geodisc + (1 - δ) * (ang_dist(ni, nj)) / avg_ang_dist
                    - ang_dist(ni, nj) = η * (1 - cos(α_avg(ni, nj))); η = 1 for α_avg >= 180 and η -> 0 for α_avg < 180
                    - geodisc(ni, nj) = distance from center of ni to center of nj

    Representation Invariant:
        - true
    
    Representation Exposure:
        - access granted to all attributes
    """
    def __init__(self, mesh, collapsed = False) -> None:
        self.mesh = mesh
        self.collapsed = collapsed
        self.faces = mesh.face_matrix()
        self.vertices = mesh.vertex_matrix()

        mesh_set = pymeshlab.MeshSet()
        mesh_set.add_mesh(pymeshlab.Mesh(mesh.vertex_matrix(), mesh.face_matrix()))
        mesh_set.compute_normal_per_face()

        self.face_objs = []
        self.face_normals = mesh_set.current_mesh().face_normal_matrix()
        self.m = self.faces.shape[0]

        print("Computing face adj ...")
        self.edge_to_faces = {}
        for i in tqdm(range(self.m)):
            v1, v2, v3 = self.faces[i]
            edge_1 = Edge(v1, v2)
            edge_2 = Edge(v2, v3)
            edge_3 = Edge(v1, v3)
            
            for edge in (edge_1, edge_2, edge_3):
                try: self.edge_to_faces[edge].append(i)
                except: self.edge_to_faces[edge] = [i]
        
        print("Computing avg_geodisc and avg_ang_dist matrix + face_objs graph ...")
        n = 0
        self.geodisc = np.zeros((self.m, self.m))
        self.ang_dist = np.zeros((self.m, self.m))
        self.face_objs = [Face([i], [[self.vertices[j] for j in self.faces[i]]]) for i in range(self.m)]

        for edge, adj in tqdm(self.edge_to_faces.items()):
            if len(adj) != 2: continue
            i, j = adj

            # Updating graph representation
            self.face_objs[i].add_adj_face(self.face_objs[j])
            self.face_objs[j].add_adj_face(self.face_objs[i])
        
        if self.collapsed:
            self.graph = self.face_objs[0].collapse(k = 1)
            self.collapsed_map = self.graph.map({})
            self.collapsed_m = self.graph.__len__(set())

        for edge, adj in tqdm(self.edge_to_faces.items()):
            if len(adj) != 2: continue
            i, j = adj
            ang_dist = self.__ang_dist(i, j)
            geodisc = self.__geodisc(_coords(self.vertices, self.faces[i]), _coords(self.vertices, self.faces[j]), edge)

            self.geodisc[i, j] = geodisc
            self.geodisc[j, i] = geodisc
            self.ang_dist[i, j] = ang_dist
            self.ang_dist[j, i] = ang_dist
            n += 2

            # Updating graph representation
            self.face_objs[i].add_adj_face(self.face_objs[j])
            self.face_objs[j].add_adj_face(self.face_objs[i])
        
        self.avg_geodisc = self.geodisc.sum() / n
        self.avg_ang_dist = self.ang_dist.sum() / n

        if self.collapsed:
            self.collapsed_geodisc = np.zeros((self.collapsed_m, self.collapsed_m))
            self.collapsed_ang_dist = np.zeros((self.collapsed_m, self.collapsed_m))

        for edge, adj in tqdm(self.edge_to_faces.items()):
            if len(adj) != 2: continue
            i, j = adj

            if self.collapsed:
                i_prime_1, i_prime_2 = self.collapsed_map[i]
                j_prime_1, j_prime_2 = self.collapsed_map[j]
            
                geodisc = self.geodisc[i_prime_1][i] + self.geodisc[i][j_prime_1] + self.geodisc[j_prime_1][j]
                ang_dist = self.__collapsed_ang_dist(i_prime_1, j_prime_1)

                self.collapsed_geodisc[i_prime_2][j_prime_2] = geodisc
                self.collapsed_ang_dist[i_prime_2][j_prime_2] = ang_dist

                self.collapsed_geodisc[j_prime_2][i_prime_2] = geodisc
                self.collapsed_ang_dist[j_prime_2][i_prime_2] = ang_dist

        if self.collapsed:
            self.avg_collapsed_geodisc = self.collapsed_geodisc.sum() / self.collapsed_geodisc.shape[0]
            self.avg_collapsed_ang_dist = self.collapsed_ang_dist.sum() / self.collapsed_ang_dist.shape[0]

        print(f"[avg_geodisc] >> {self.avg_geodisc}")
        print(f"[avg_ang_dist] >> {self.avg_ang_dist}")

        if self.collapsed:
            print(f"[avg_collapsed_geodisc] >> {self.avg_collapsed_geodisc}")
            print(f"[avg_collapsed_ang_dist] >> {self.avg_collapsed_ang_dist}")
        
        self.__construct_adj_matrix()
        self.__construct_degree_matrix()

        if self.collapsed:
            self.__construct_collapsed_adj_matrix()
            self.__construct_collapsed_degree_matrix()
    
    def similarity_matrix(self, k = 1, collapsed = False):
        """
        Computes the similairty matrix of the graph which is of size m // k x m // k
        Inputs
            :k: <int> condensation factor
        """
        print("Computing similarity matrix ...")
        # Convert matrix to linked list graph and use parent/child relationship in order to collapse graph by factor of k
        start_time = time()
        if collapsed:
            matrix = scipy.sparse.csgraph.dijkstra(self.collapsed_adj_matrix)
            print(f"Computed collapsed similarity in {time() - start_time}")
        else: 
            matrix = scipy.sparse.csgraph.dijkstra(self.adj_matrix)
            print(f"Computed similarity in {time() - start_time}")

        inf_indices = np.where(np.isinf(matrix))
        matrix[inf_indices] = 0
        
        sigma = matrix.mean()
        print(f"[sigma] >> {sigma}")
        np.exp(-matrix / (2 * (sigma ** 2)))
        np.fill_diagonal(matrix, 1)
        return matrix

    def get_collapsed(self):
        """ 
        Returns the collapsed mesh 
        
        Outputs
            :returns: <list, list> representation of the collapsed mesh's vertices, faces
        """
        face_to_vert = {}
        for i, j in self.collapsed_map.items():
            try: face_to_vert[j[1]] |= set([v for v in self.faces[i]])
            except: face_to_vert[j[1]] = set([v for v in self.faces[i]])
        
        collapsed_faces = [0]*len(face_to_vert)
        for face, verts in face_to_vert.items():
            verts = list(verts)
            collapsed_faces[face] = verts
        
        return list(self.vertices), collapsed_faces


    ### Helper Methods ###
    def __construct_adj_matrix(self):
        """ Construct the m x m adjacency matrix """
        print("Computing face graph adjacency matrix ...")
        self.adj_matrix = self.__weights(delta = 0.03)
    
    def __construct_collapsed_adj_matrix(self):
        """ Construct the m x m adjacency matrix """
        print("Computing collapsed face graph adjacency matrix ...")
        self.collapsed_adj_matrix = self.__collapsed_weights(delta = 0.03)

    def __weights(self, delta = 0.03):
        """ Compute the weights matrix where weight of face_1 --- face_2 = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist"""
        self.geodisc *= delta / self.avg_geodisc
        self.geodisc += (1 - delta) * self.ang_dist / self.avg_ang_dist
        return self.geodisc

    def __collapsed_weights(self, delta = 0.03):
        """ Compute the weights matrix where weight of face_1 --- face_2 = δ * (geodisc(fi, fj)) / avg_geodisc + (1 - δ) * (ang_dist(fi, fj)) / avg_ang_dist"""
        self.collapsed_geodisc *= delta / self.avg_collapsed_geodisc
        self.collapsed_geodisc += (1 - delta) * self.collapsed_ang_dist / self.avg_collapsed_ang_dist
        return self.collapsed_geodisc

    def __geodisc(self, face_1, face_2, edge):
        """ Computes the geodistance between the centers of face_1 and face_2 over the edge"""
        edge_center = edge.mean(self.vertices)
        return np.linalg.norm(edge_center - face_1.mean(0)) + np.linalg.norm(edge_center - face_2.mean(0))
    
    def __ang_dist(self, i, j, eta = 0.15):
        """ Computes the angular distance between face_1 and face_2 = η * (1 - cos(α(fi, fj))); η = 1 for α >= 180 and η -> 0 for α < 180"""
        face_1 = self.faces[i]
        face_2 = self.faces[j]
        face_1_normal = self.face_normals[i]
        face_2_normal = self.face_normals[j]
        
        cos_alpha = np.dot(face_1_normal, face_2_normal) / np.linalg.norm(face_1_normal) / np.linalg.norm(face_2_normal)
        
        if not np.all(face_1_normal.dot(face_2.mean() - face_1.mean())) < 0: eta = 1
        return eta * (1 - cos_alpha)

    def __collapsed_ang_dist(self, i, j, eta = 0.15):
        """ Computes the angular distance between node_1 and node_2 = η * (1 - cos(α_avg(fi, fj))); η = 1 for α_avg >= 180 and η -> 0 for α_avg < 180"""
        node_1 = self.face_objs[i]
        node_2 = self.face_objs[j]

        node_1_normal = self.face_normals[node_1.i[0]]
        for face in node_1.faces: node_1_normal += self.face_normals[face.i[0]]
        node_1_normal /= (len(node_1.faces) + 1)

        node_2_normal = self.face_normals[node_2.i[0]]
        for face in node_2.faces: node_2_normal += self.face_normals[face.i[0]]
        node_2_normal /= (len(node_2.faces) + 1)
    
        cos_alpha = np.dot(node_1_normal, node_2_normal) / np.linalg.norm(node_1_normal) / np.linalg.norm(node_2_normal)
        # if cos_alpha >= 1: print(f"[cos_ alpha > 1!] >> {cos_alpha}")
        if not np.all(node_1_normal.dot(node_2.mean() - node_1.mean())) < 0: eta = 1
        return eta * (1 - cos_alpha)

    def __construct_degree_matrix(self):
        """ Construct the m x 1 degree matrix """
        self.degree_matrix = np.reciprocal(self.adj_matrix.sum(1))
    
    def __construct_collapsed_degree_matrix(self):
        self.collapsed_degree_matrix = np.reciprocal(self.collapsed_adj_matrix.sum(1))
