import clip
import argparse
from main import x2mesh
from utils import device

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    clip_model, preprocess = clip.load('ViT-B/32', device, jit=False)
    
    ### render settings
    parser.add_argument('--n_views', type=int, default=5)

    ### run settings
    parser.add_argument('--n_augs', type=int, default=0)
    parser.add_argument('--geoloss', action="store_true")
    parser.add_argument('--decay', type=float, default=0)
    parser.add_argument('--lr', type=float, default=0.0005)
    parser.add_argument('--lr_decay', type=float, default=1)
    parser.add_argument('--n_normaugs', type=int, default=0)
    parser.add_argument('--lr_plateau', action='store_true')
    parser.add_argument('--decay_step', type=int, default=100)
    parser.add_argument('--decay_freq', type=int, default=None)
    parser.add_argument('--crop_decay', type=float, default=1.0)
    parser.add_argument('--split_norm_loss', action="store_true")
    parser.add_argument('--symmetry', default=False, action='store_true')
    parser.add_argument('--output_dir', type=str, default='round2/alpha5')
    parser.add_argument('--obj_path', type=str, default='meshes/mesh1.obj')
    parser.add_argument('--standardize', default=False, action='store_true')
    parser.add_argument('--verticies_in_file', default=False, action='store_true')
    parser.add_argument('--vertices_to_not_change', type=str, default="vertices.txt")


#     run_parser.add_argument('--prompt_list', nargs="+", default=None)
    parser.add_argument('--norm_prompt_list', nargs="+", default=None)
    parser.add_argument('--train_type', type=str, default="shared")
    parser.add_argument('--norm_sigma', type=float, default=10.0)
    parser.add_argument('--norm_width', type=int, default=256)
    parser.add_argument('--normal_learning_rate', type=float, default=0.0005)
    parser.add_argument('--encoding', type=str, default='gaussian')
    parser.add_argument('--norm_encoding', type=str, default='xyz')
    parser.add_argument('--layernorm', action="store_true")
    parser.add_argument('--run', type=str, default=None)
    parser.add_argument('--gen', action='store_true')
    parser.add_argument('--frontview', action='store_true')
    parser.add_argument('--frontview_std', type=float, default=8)
    parser.add_argument('--frontview_center', nargs=2, type=float, default=[0., 0.])
    parser.add_argument('--clipavg', type=str, default=None)
    parser.add_argument('--samplebary', action="store_true")
#     run_parser.add_argument('--prompt_views', nargs="+", default=None)
    parser.add_argument('--split_color_loss', action="store_true")
    parser.add_argument("--no_norm", action="store_true")
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--background', nargs=3, type=float, default=None)
    parser.add_argument('--save_render', action="store_true")

    ### initiation settings
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--depth', type=int, default=4)
    parser.add_argument('--exclude', type=int, default=0)
    parser.add_argument('--width', type=int, default=256)
    parser.add_argument('--image', type=str, default=None)
    parser.add_argument('--n_iter', type=int, default=6000)
    parser.add_argument('--sigma', type=float, default=10.0)
    parser.add_argument('--norm_depth', type=int, default=2)
    parser.add_argument('--clamp', type=str, default="tanh")
    parser.add_argument('--crop_steps', type=int, default=0)
    parser.add_argument('--min_crop', type=float, default=1)
    parser.add_argument('--max_crop', type=float, default=1)
    parser.add_argument('--color_depth', type=int, default=2)
    parser.add_argument('--crop_forward', action='store_true')
    parser.add_argument('--norm_ratio', type=float, default=0.1)
    parser.add_argument('--norm_clamp', type=str, default="tanh")
    parser.add_argument('--norm_prompt', nargs="+", default=None)
    parser.add_argument('--norm_min_crop', type=float, default=0.1)
    parser.add_argument('--norm_max_crop', type=float, default=0.1)
    parser.add_argument('--only_z', default=False, action='store_true')
    parser.add_argument('--prompt', nargs="+", default='a pig with pants')
    parser.add_argument('--no_prompt', default=False, action='store_true')
    parser.add_argument('--input_normals', default=False, action='store_true')
    parser.add_argument('--no_pe', dest='pe', default=True, action='store_false')
    
    args = parser.parse_args()
    x2mesh(args, clip_model, preprocess)
    