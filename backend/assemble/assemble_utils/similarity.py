import os
import pymeshlab
from time import sleep
import shlex, subprocess
from io import BytesIO

### Global Constants ###
reeb_graph = "/home/ubuntu/fa3ds/backend/assemble/assemble_utils/reeb_graph"
models_dir = "/home/ubuntu/fa3ds/backend/assemble/assemble_utils/models"
wrl_header = \
"""
#VRML V2.0 utf8
WorldInfo {
    info [
        "This file was created by the GICL Sat2Vrml program",
        "http://gicl.mcs.drexel.edu/",
        "Drexel University",
        "Released under the GNU GPL",
        "Copyright (C) 2001 Daniel Lapadat"
    ]
    title "GICL Sat2Vrml"
}
Viewpoint {
    fieldOfView 0.785398
    position 50 50 300
    orientation 0 0 1 0
    description "Front"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position 50 50 -200
    orientation 1 0 0 3.141593
    description "Back"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position 300 50 50
    orientation 0 1 0 1.570796
    description "Right Side"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position -200 50 50
    orientation 0 1 0 -1.570796
    description "Left Side"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position 50 300 50
    orientation 1 0 0 -1.570796
    description "Top"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position 50 -200 50
    orientation 1 0 0 1.570796
    description "Bottom"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position 200 200 200
    orientation 1 -1 0 -1.047198
    description "Diagonal Top"
    jump TRUE
}
Viewpoint {
    fieldOfView 0.785398
    position -100 -100 -100
    orientation 1 -1 0 2.094395
    description "Diagonal Bottom"
    jump TRUE
}
NavigationInfo {
    avatarSize [0.25, 1.6, 0.75]
    headlight TRUE
    speed 1.0
    type ["EXAMINE", "ANY"]
    visibilityLimit 0.0
}
Transform {
        children [
            Shape {
                geometry IndexedFaceSet {
                    coord Coordinate {
                        point [
"""
wrl_end_point = \
"""
                    ] #end of point
                } #end of Coordinate
                coordIndex [
"""
wrl_footer = \
"""
                ] #end of coordIndex
            } #end of geometry
            appearance Appearance {
                material Material {
                    diffuseColor 0.7 0.7 0.7
                    emissiveColor 0.05 0.05 0.05
                    specularColor 1.0 1.0 1.0
                    ambientIntensity 0.2
                    shininess 0.2
                    transparency 0.0
                } #end of material
            } #end of appearance
        } #end of Shape
    ] #end of children
}
"""

def similarity(mesh_set, wait = None, arg1 = 4000, mu = 0.0005, arg2 = 128, arg3 = 0.5):
    """
    Computes the similarities between a set of meshes

    Inputs
        :mesh_set: <pymeshlab.MeshSet> a set of meshes to be evaluated for similarity
        :arg1: <float>
        :mu: <float>
        :arg2: <float>
        :arg3: <float>

    Outputs
        :returns: <dict> mapping mesh -> most similar other mesh
    """
    sims = []
    model_paths = []
    for i, mesh in enumerate(mesh_set):
        faces, vertices = mesh.face_matrix(), mesh.vertex_matrix()
        print(f"[faces] >> ({type(faces)}) ({faces.shape})")
        print(f"[vertices] >> ({type(vertices)}) ({vertices.shape})")
        model_path = f"{models_dir}/model_{i}.wrl"

        model_paths.append(model_path)
        _save_as_wrl(faces, vertices, model_path)

    command_0 = "echo " + "\n".join(model_path for model_path in model_paths)
    process_0 = _exec(command_0, keep_output = True)

    command_1 = f"xargs  java -cp \"{reeb_graph}/src/\" -Xmx16384m ExtractReebGraph {arg1} {mu} {arg2}"
    process_1 = _exec(command_1, stdin = process_0.stdout, wait = wait)
        
    command_0 = "echo " + "\n".join(model_path for model_path in model_paths)
    process_0 = _exec(command_0, keep_output = True)
    
    command_2 = f"xargs  java -cp \"{reeb_graph}/src/\" -Xmx16384m CompareReebGraph {arg1} {mu} {arg2} {arg3}"
    process_2 = _exec(command_2, stdin = process_0.stdout, wait = wait)

    out = process_2.split("\n")
    for line in out:
        try:
            model_1, model_2, sim = line.split(",")
        except: continue
        name_1, _ = os.path.splitext(model_1)
        name_2, _ = os.path.splitext(model_2)
        name_1, name_2 = name_1.split("/")[-1], name_2.split("/")[-1]

        sims.append(sim)
        print(f"[out] >> {name_1} ~ {name_2} = {float(sim):.3f}")
    
    _exec(f"rm -rf {models_dir}")
    _exec(f"mkdir {models_dir}")

    for i, mesh in enumerate(mesh_set):
        mesh_set.set_current_mesh(i)
        mesh_set.save_current_mesh(f"{models_dir}/model_{i}.obj")
    
    return sims

### Helper Functions ###
def _exec(command: str, wait: int = None, stdin = None, keep_output = False) -> subprocess:
    """
    Executes a command using a subprocess and returns the execution subprocess

    Inputs
        :command: <str> command to execute 
        :wait: <int> amount of time to wait for command to execute
    
    Outputs
        :subprocess: <subprocess> a sub-process that runs the executed command
    """
    # print(f"[cmd] >> {command}")
    command = shlex.split(command)
    if not keep_output: 
        process = ""
        for out in _run(stdin, command):
            print(out, end="")
            process += f"{out}\n"
    else: process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=stdin, universal_newlines=True)
        
        
    if wait is not None: sleep(wait)
    print("--- Done ---")
    return process

def _run(stdin, command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stdin=stdin, universal_newlines=True)
    for stdout_line in iter(process.stdout.readline, ""):
        yield stdout_line 
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)
    
def _save_as_wrl(faces, vertices, path):
    """
    Export given list of Mesh objects to a VRML file.

    Inputs
        :faces: <np.ndarray> of size (f, 3) for f faces
        :vertices: <np.ndarray> of size (v, 3) for v vertices
        :path: path to store vrml to 
    """
    # print("Converting to wrl ...")
    with open(path, 'w') as wrl:
        # write the standard VRML header
        wrl.write(wrl_header)

        #write coordinates (x, y, z) for each vertex
        wrl.write("\t\t\t\t\t\t" + "\n\t\t\t\t\t\t".join(f"{v[0]:.3f} {v[1]:.3f} {v[2]:.3f}," for v in vertices))
        wrl.write(wrl_end_point)
        
        # write vertex indexes for each face
        wrl.write("\t\t\t\t\t\t" + "\n\t\t\t\t\t\t".join(f"{f[0]}, {f[1]}, {f[2]}, -1," for f in faces))
        wrl.write(wrl_footer) 
    # print("--- Done ---")

if __name__ == "__main__":
    # mesh_path_1 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_0.0/segment_0.0.obj"
    # mesh_path_2 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_1.0/segment_1.0.obj"
    # mesh_path_3 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_2.0/segment_2.0.obj"
    # mesh_path_4 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_3.0/segment_3.0.obj"
    # mesh_path_5 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_4.0/segment_4.0.obj"
    # mesh_path_6 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_5.0/segment_5.0.obj"
    # mesh_path_7 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_6.0/segment_6.0.obj"
    # mesh_path_8 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_7.0/segment_7.0.obj"
    # mesh_path_9 = "/home/ubuntu/fa3ds/backend/results/study_models/component_0_model_15/segment_8.0/segment_8.0.obj"
    alpaca = "/home/ubuntu/fa3ds/backend/results/user_study/alpaca"
    cat = "/home/ubuntu/fa3ds/backend/results/user_study/cat"
    fillacutter = "/home/ubuntu/fa3ds/backend/results/user_study/fillacutter_base"
    horse = "/home/ubuntu/fa3ds/backend/results/user_study/horse"
    
    log = "/home/ubuntu/fa3ds/backend/results/user_study/similarity.csv"
    meshes = [fillacutter, alpaca, cat, horse]
    for mesh in meshes:
        components = []
        n = len(os.listdir(mesh))
        for k1 in range(n):
            component_1 = f"{mesh}/model_{k1}"
            m1 = len([1 for segment in os.listdir(component_1) if os.path.isdir(f"{component_1}/{segment}")])
            for i in range(m1):
                for k2 in range(k1 + 1, n):
                    component_2 = f"{mesh}/model_{k2}"
                    m2 = len([1 for segment in os.listdir(component_2) if os.path.isdir(f"{component_2}/{segment}")])
                    for j in range(m2):
                        ms = pymeshlab.MeshSet()
                        ms.load_new_mesh(f"{component_1}/segment_{i}.0/segment_{i}.0.obj")
                        ms.load_new_mesh(f"{component_2}/segment_{j}.0/segment_{j}.0.obj")
                        sims = similarity(ms)
                        ms.clear()
                        with open(log, "a") as log_file:
                            log_file.write(f"{component_1},{component_2},{i},{j},{sims[1]}\n")
                            log_file.write(f"{component_2},{component_1},{j},{i},{sims[1]}\n")