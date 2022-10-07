import os
import clip
import torch
import random 
import numpy as np
from PIL import Image
from ..mesh import Mesh
from pathlib import Path
from ..utils import device
from ..neural_style_field import NeuralStyleField

def _initiate(clip_model, preprocess, args):
    """
    Initiates a stylization process by fetching and processing the mesh_path, starting the neural style field, and
    creating the output directories

    Inputs
        :args: <dict> map of arguments passed to network through shell script

    Outputs
        :returns: <Mesh> object representing the mesh, <NSF> network to preform the sylization on the mesh, 
                <str> path of directories storing results, <tensor> encoded image, <tensor> encoded text
    """
    mesh_path = args['obj_path']
    __constrain_randomness(args)
    output_dir = args['output_dir']

    mesh = Mesh(mesh_path)
    Path(args['output_dir']).mkdir(parents=True, exist_ok=True)
    mesh_name, extension = os.path.splitext(os.path.basename(mesh_path))
    
    final_dir = os.path.join(output_dir, f"{mesh_name}_final_style")
    iters_dir = os.path.join(output_dir, f"{mesh_name}_iters_style")
    final_dir = __create_dir(final_dir)
    iters_dir = __create_dir(iters_dir)
    
    with open(f"{final_dir}/args.txt", 'w') as arg_file:
        arg_file.write(str(args))
        arg_file.close()
    
    if args['crop_forward'] : crop_cur = args['norm_min_crop']
    else: crop_cur = args['norm_max_crop']
   
    crop_update = 0
    if args['norm_min_crop'] < args['norm_max_crop'] and args['crop_steps'] > 0:
        crop_update = (args['max_crop'] - args['min_crop']) / round(args['n_iter'] / (args['crop_steps'] + 1))
        if not args['crop_forward']: crop_update *= -1
    
    input_dim = 6 if args['input_normals'] else 3
    if args['only_z']: input_dim = 1
    nsf = NeuralStyleField(args['sigma'], args['depth'], args['width'], 'gaussian', args['color_depth'], args['norm_depth'],
                           args['norm_ratio'], args['clamp'], args['norm_clamp'], niter=args['n_iter'],
                           progressive_encoding=args['pe'], input_dim=input_dim, exclude=args['exclude']).to(device)
    nsf.reset_weights()
    
    
    encoded_text = None
    encoded_norm = None
    encoded_image = None
    
    if args['prompt']:
        prompt = ' '.join(args['prompt'])
        prompt_token = clip.tokenize([prompt]).to(device)
        encoded_text = clip_model.encode_text(prompt_token) # Text being tokenized by CLIP

        # Same with normprompt
        encoded_norm = encoded_text

    if args['norm_prompt'] is not None:
        prompt = ' '.join(args['norm_prompt'])
        prompt_token = clip.tokenize([prompt]).to(device)
        encoded_norm = clip_model.encode_text(prompt_token)

        # Save prompt
        with open(os.path.join(output_dir, f"NORM {prompt}"), "w") as f: f.write("")
    
    if args['image']:
        img = Image.open(args['image'])
        img = preprocess(img).to(device)
        encoded_image = clip_model.encode_image(img.unsqueeze(0))
        if args['no_prompt']: encoded_norm = encoded_image
    
    return mesh, nsf, (final_dir, iters_dir), (encoded_image, encoded_text, encoded_norm), crop_cur, crop_update

def _construct_mask(vertices, mesh, file = True):
    """
    Constructs a mask for the mesh

    Inputs
        :vertices: <str> to file containing indices of vertices of interest
        :mesh: <Mesh> to be construct a mask for
    """
    voi = [] # verticies of interest
    if file: 
        with open(vertices, "r") as vertices:
            vertices = vertices.readlines()
    
    for vertex in vertices:
        try: voi.append(int(vertex))
        except Exception: pass


    print(f"{len(voi)} vertices will not be changed")

    mask = torch.ones(mesh.vertices.shape).to(device)
    for j in range(len(mesh.vertices)):
        if j in voi: mask[j, ::] = torch.zeros((3))
    
    return mask

### Helper Functions ###
def __create_dir(dir_path):
    """Creates a dir, ensuring if the path exists we make an ith copy"""
    i = 0
    new_dir_path = f"{dir_path}_{i}"
    while os.path.isdir(new_dir_path):
        i += 1
        new_dir_path = f"{dir_path}_{i}"
    os.mkdir(new_dir_path)
    print(f"Saving to {new_dir_path} ...")
    return new_dir_path

def __constrain_randomness(args):
    """Constrains all sources of randomness"""
    random.seed(args['seed'])
    np.random.seed(args['seed'])
    torch.manual_seed(args['seed'])
    torch.cuda.manual_seed(args['seed'])
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.cuda.manual_seed_all(args['seed'])
