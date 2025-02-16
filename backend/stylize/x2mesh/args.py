args = {
    ### render settings
    'n_views': 5,

    ### run settings
    'n_augs': 1,
    'geoloss': True,
    'decay': 0,
    'lr': 0.0005,
    'lr_decay': 1,
    'n_normaugs': 4,
    'lr_plateau': True,
    'decay_step': 100,
    'decay_freq': None,
    'crop_decay': 1.0,
    'split_norm_loss': True,
    'symmetry': True,
    'output_dir': "results/",
    'obj_path': "meshes/mesh1.obj",
    'standardize': True,
    'verticies_in_file': True,
    'selected_vertices': "vertices.txt",
    'mesh_type': "obj",

    'norm_prompt_list': None,
    'train_type': "shared",
    'norm_sigma': 10.0,
    'norm_width': 256,
    'normal_learning_rate': 0.0005,
    'encoding': "gaussian",
    'norm_encoding': "xyz",
    'layernorm': True,
    'run': "branch",
    'gen': True,
    'frontview': True,
    'frontview_std': 4,
    'frontview_center': [0., 0.],
    'clipavg': "view",
    'samplebary': True,
    'split_color_loss': True,
    'no_norm': True,
    'overwrite': True,
    'show': True,
    'background': [1, 1, 1],
    'save_render': True,

    ### initiation settings
    'seed': 29,
    'depth': 4,
    'exclude': 0,
    'width': 256,
    'image': None,
    'n_iter': 6000,
    'sigma': 10.0,
    'norm_depth': 2,
    'clamp': "tanh",
    'crop_steps': 0,
    'min_crop': 1,
    'max_crop': 1, 
    'color_depth': 2,
    'crop_forward': True,
    'norm_ratio': 0.1,
    'norm_clamp': "tanh",
    'norm_prompt': None,
    'norm_min_crop': 0.1,
    'norm_max_crop': 0.4,
    'only_z': False,
    'prompt': "a duck with pants",
    'no_prompt': False,
    'input_normals': False, 
    'pe': True
}