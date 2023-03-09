import os
import pymeshlab

### Global Constants ###
exts = [".obj"]

def standarize(mesh_dir, face_count = 5000):
    """ Standarizes the number of faces in all meshes in given mesh_dir """
    for _, dirs, files in os.walk(mesh_dir):
        for dir in dirs: standarize(f"{mesh_dir}/{dir}")
        for file in files: 
            mesh_name, mesh_ext = os.path.splitext(file)
            if mesh_ext not in exts: continue
            print(f"Preprocessing {mesh_dir}/{file} ...")

            ms = pymeshlab.MeshSet()
            ms.load_new_mesh(f"{mesh_dir}/{file}")

            print(f"\tcollapsing {ms.current_mesh().face_matrix().shape[0]} -> {face_count} ...")
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=face_count)
            print(f"\tremeshing ...")
            ms.meshing_isotropic_explicit_remeshing(iterations=3)
            print(f"\tcollapsing {ms.current_mesh().face_matrix().shape[0]} -> {face_count} ...")
            ms.meshing_decimation_quadric_edge_collapse(targetfacenum=face_count)
            print(f"--- Done ---")
            
            ms.save_current_mesh(f"{mesh_dir}/{file}")
            ms.clear()

if __name__ == "__main__":
    mesh_dir = "/home/ubuntu/scraped_models/first_100_models_files"
    standarize(mesh_dir)