import numpy as np

class Face():
    def __init__(self, i, vertices) -> None:
        self.i = i
        self.faces = []
        self.adj_faces = []
        self.vertices = vertices
    
    def add_adj_face(self, face):
        """ Requires every face has at most 2 adjacent faces """
        # print(f"Adding {face} to {self}")
        if face in self.adj_faces: return
        if len(self.adj_faces) == 3: raise ValueError("Adjacent faces should not be > 2")
        self.adj_faces.append(face)
        # print(f"{face} added to {self}, size of adjacent faces is now {len(self.adj_faces)}")

    def mean(self):
        """ Compute the mean of the face """
        mean = np.array(self.vertices)
        for face in self.faces:
            mean += np.array(face.vertices)
        return mean.mean() / (len(self.faces) + 1)
            

    def collapse(self, k: int = 0, seen = set()):
        """ Collapses face unto its children, k = log(n) where n is the number of collopsed elements """
        if self in seen: return self
        seen.add(self)

        if k > 1: raise ValueError("Not yet equiped to handle k > 1 (n > 2)")

        if k == 0: 
            return self
        
        collapsed_face = Face(self.i, [self.vertices])
        if k == 1:
        # self.adj_faces = []
            for child in self.adj_faces:
                if child in seen: continue
                collapsed_face.merge(child)
                seen.add(child)

        
        collapsed_childern = []
        for child in collapsed_face.adj_faces:
            if child in seen: continue
            collapsed_child = child.collapse(k, seen)
            collapsed_childern.append(collapsed_child)

        collapsed_face.adj_faces = collapsed_childern
        return collapsed_face
    
    def merge(self, face):
        """ Merges two faces to become one """
        self.i += face.i
        self.faces.append(face)
        self.adj_faces += face.adj_faces

    def map(self, map = {}):
        """  """
        map[self.i[0]] = [self.i[0], max([v[1] for _, v in map.items()]) + 1] if len(map) > 1 else [self.i[0], self.i[0]]
        for face in self.faces:
            map[face.i[0]] = map[self.i[0]]
        
        for child in self.adj_faces:
            if child.i[0] in map: continue
            child.map(map)
        return map
        
    def __iter__(self):
        for v in self.vertices: yield v
    
    def __len__(self, seen = set()):
        size = 1
        seen.add(self)
        for child in self.adj_faces:
            if child in seen: continue
            size += child.__len__(seen)
            seen.add(child)
        return size

    def __str__(self) -> str:
        return f"Face {self.i}"
