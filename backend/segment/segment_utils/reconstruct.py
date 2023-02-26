import os
import pymeshlab
import numpy as np

### Constants ###
txt =".txt"
mesh_ext = [".obj"]
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

def reconstruct_mesh(path, mesh_name = "reconstructed_mesh"):
    """
    Reconstructs a mesh from its segments

    Inputs
        :path: <str> Path to the directory containing the segments
    
    Outputs
        :return: <None> Saves the reconstructed mesh to the directory containing the segments
    """
    # (f', s) -> f | f in mesh_faces, f' in faces_segment_s
    face_map = {}
    
    # create a new MeshSet
    ms = pymeshlab.MeshSet()

    # add all face index and segment number data to face_map and add the segments to the MeshSet
    for segmentation_dir in sorted(os.listdir(path)):
        # print(f"[reconst] >> {path}/{segmentation_dir}")
        if not os.path.isdir(f"{path}/{segmentation_dir}"): continue
        for segment_file in os.listdir(f"{path}/{segmentation_dir}"):
            # print(f"[reconst.seg] >> {path}/{segmentation_dir}")
            segment_name, segment_ext = os.path.splitext(segment_file)
            if segment_ext in mesh_ext:
                ms.load_new_mesh(f"{path}/{segmentation_dir}/{segment_file}")
                continue
            elif not segment_ext == txt: continue
            
            with open(f"{path}/{segmentation_dir}/{segment_file}", "r") as segment:
                segment_lines = segment.readlines()
                for line in segment_lines[3:]:
                    line = line.split()
                    face_map[(int(line[0]), int(float(segmentation_dir.split('_')[-1])))] = int(line[2])

    vert_map = {}
    vertices = []
    faces = np.zeros((len(face_map), 3))
    face_segments = np.zeros((len(face_map),))
    f_color_matrix = np.zeros((len(face_map), 4))
    
    for i, mesh in enumerate(ms):
        vertex_matrix = mesh.vertex_matrix()
        for j, face in enumerate(mesh.face_matrix()):
            for k, v in enumerate(face):
                if tuple(vertex_matrix[v]) not in vert_map: 
                    vert_map[tuple(vertex_matrix[v])] = len(vert_map)
                    vertices.append(vertex_matrix[v])
                face[k] = vert_map[tuple(vertex_matrix[v])]             
            f = face_map[(j, i)]
            face_segments[f] = i
            faces[f] = face
            f_color_matrix[f] = colors[i][1]   
    
    vertices = np.array(vertices)
    new_mesh = pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=faces, f_color_matrix=f_color_matrix)

    ms.add_mesh(new_mesh)
    ms.save_current_mesh(f"{path}/{mesh_name}.obj")

    return new_mesh, face_segments

# if __name__ == "__main__":
#     mesh_dir = "/home/ubuntu/segmented_models/3d_printed_mechanical_clock_with_anchor_escapement_328569/component_2_crank_gear_reduction/5_segmentation"
#     new_mesh, face_segments = reconstruct_mesh(mesh_dir, mesh_name = "reconstructed_mesh")
