import re
import pymeshlab
import numpy as np
from itertools import chain, combinations

### Global Constants ###
colors = {
    0: ["blue", (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1)],
    1: ["violet", (0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 1)],
    3: ["green", (0.0, 0.5019607843137255, 0.0, 1)],
    2: ["brown", (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1)],
    4: ["yellow", (1.0, 1.0, 0.0, 1)],
    5: ["red", (0.803921568627451, 0.3607843137254902, 0.3607843137254902, 1)],
    6: ["white", (1.0, 1.0, 1.0, 1)],
    7: ["gray", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1)],
    8: ["purple", (0.5019607843137255, 0.0, 0.5019607843137255, 1)],
    9: ["dark blue", (0.09803921568627451, 0.09803921568627451, 0.4392156862745098, 1)],
    10: ["light green", (0.48627450980392156, 0.9882352941176471, 0.0, 1)],
    11: ["gold", (1.0, 0.8431372549019608, 0.0, 1)],
    12: ["blue II", (0.2549019607843137, 0.4117647058823529, 0.8823529411764706, 1)],
    13: ["violet II", (0.5411764705882353, 0.16862745098039217, 0.8862745098039215, 1)],
    14: ["brown II", (0.5450980392156862, 0.27058823529411763, 0.07450980392156863, 1)],
    15: ["green II", (0.0, 0.5019607843137255, 0.0, 1)],
    16: ["yellow II", (1.0, 1.0, 0.0, 1)],
    17: ["red I", (0.803921568627451, 0.3607843137254902, 0.3607843137254902, 1)],
    18: ["white II", (1.0, 1.0, 1.0, 1)],
    19: ["gray II", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255, 1)],
    20: ["purple II", (0.5019607843137255, 0.0, 0.5019607843137255, 1)],
    21: ["dark blue II", (0.09803921568627451, 0.09803921568627451, 0.4392156862745098, 1)],
    22: ["light green II", (0.48627450980392156, 0.9882352941176471, 0.0, 1)],
    23: ["gold II", (1.0, 0.8431372549019608, 0.0, 1)],
    24: ["gold III", (1.0, 0.8431372549019608, 0.0, 1)],
}
models_dir = "/home/ubuntu/fa3ds/backend/assemble/assemble_utils/models"
replace_mult = lambda s, replaced, replacee: s.replace(replaced[0], replacee[0]) if len(replaced) == 1 else replace_mult(s.replace(replaced[0], replacee[0]), replaced[1:], replacee[1:])

def assemble(mesh_set, mesh_name = "assembled"):
    """
    Assembles a set of meshes into a single mesh

    Inputs
        :mesh_set: <pymeshlab.MeshSet()> 
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
    f_color_matrix = np.array(f_color_matrix)

    # print(f"[faces] >> {faces.shape}")
    # print(f"[vertices] >> {vertices.shape}")
    # print(f"[f_color_matrix] >> {f_color_matrix.shape}")

    new_mesh = pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=faces, f_color_matrix=f_color_matrix)

    # ms.add_mesh(new_mesh)
    # ms.save_current_mesh(f"{models_dir}/{mesh_name}.obj")

    return new_mesh

def generate_power_set(mesh_set):
    """
    Takes a set of segments and generates segment super set 
    Let ...
        ... S = {segment for segment in segments}
    We want to compute the super set of S, that is 
    Super_S = {(segment_i, segment_j, ...) for all possible combination of segments}

    Inputs
        :mesh_set: <pymeshlab.MeshSet()> a set of meshses

    Outputs
        :returns: <pymeshlab.MeshSet()> super set of mesh_set
    """
    mesh_set_indicies = [i for i in range(len(mesh_set))]
    m = len(mesh_set_indicies)   

    power_set = list(chain.from_iterable(combinations(mesh_set_indicies, i) for i in range(m + 1)))
    
    power_mesh_set = pymeshlab.MeshSet()
    for i, sub_set in enumerate(power_set):
        if len(sub_set) == 0: continue
        ms = pymeshlab.MeshSet()
        for j in sub_set: ms.add_mesh(mesh_set[j])
        name = replace_mult(f"assembled_{sub_set}", [")", "(", ",", " "], ["", "", "_", ""])

        power_mesh_set.add_mesh(assemble(ms, name))
        ms.clear()
  
    return power_mesh_set

# if __name__ == "__main__":
#     mesh_path_1 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_7/segment_7.obj"
#     mesh_path_2 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_4/segment_4.obj"
#     mesh_path_3 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_2/segment_2.obj"
#     mesh_path_4 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_0/segment_0.obj"
#     mesh_path_5 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_1/segment_1.obj"
#     mesh_path_6 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_3/segment_3.obj"
#     mesh_path_7 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_5/segment_5.obj"
#     mesh_path_8 = "/home/ubuntu/fa3ds/backend/results/api_segmented_models/model_1/8_segmentation/segment_6/segment_6.obj"
#     ms = pymeshlab.MeshSet()
#     ms.load_new_mesh(mesh_path_1)
#     ms.load_new_mesh(mesh_path_2)
#     ms.load_new_mesh(mesh_path_3)
#     ms.load_new_mesh(mesh_path_4)
#     ms.load_new_mesh(mesh_path_5)
#     ms.load_new_mesh(mesh_path_6)
#     ms.load_new_mesh(mesh_path_7)
#     ms.load_new_mesh(mesh_path_8)
#     power_set = generate_power_set(ms)
    # assemble(ms)
                

    
