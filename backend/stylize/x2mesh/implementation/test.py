import torch
import kaolin as kal
from .utils import device
from torchvision import transforms

### Global Constants ###
norm_1 = (0.48145466, 0.4578275, 0.40821073)
norm_2 = (0.26862954, 0.26130258, 0.27577711)
clip_normalizer = transforms.Normalize(norm_1, norm_2)
clip_transform = transforms.Compose([transforms.Resize((224, 224)), clip_normalizer])

loss_3 = lambda encoded_renders, encoded_input: torch.mean(torch.cosine_similarity(encoded_renders, encoded_input))
loss_2 = lambda encoded_renders, encoded_input: torch.cosine_similarity(torch.mean(encoded_renders, dim=0, keepdim=True), encoded_input)
loss_1 = lambda encoded_renders, encoded_input: torch.cosine_similarity(torch.mean(encoded_renders, dim=0), torch.mean(encoded_input, dim=0), dim=0)

aug_transform = transforms.Compose([transforms.RandomResizedCrop(224, scale=(1, 1)), transforms.RandomPerspective(fill=1, p=0.8, distortion_scale=0.5), clip_normalizer])
normaug_transform = lambda crop_cur: transforms.Compose([transforms.RandomResizedCrop(224, scale=(crop_cur, crop_cur)), transforms.RandomPerspective(fill=1, p=0.8, distortion_scale=0.5), clip_normalizer])
displaug_transform = lambda norm_min_crop: transforms.Compose([transforms.RandomResizedCrop(224, scale=(norm_min_crop, norm_min_crop)), transforms.RandomPerspective(fill=1, p=0.8, distortion_scale=0.5), clip_normalizer])

def test(nsf, mesh, renderer, encodings, clip_model, optimizer, losses, norm_weight, crop_update, args, i):
    """
    Tests the nsf model on the mesh and reports the loss and normal loss

    Inputs
        :nsf: <NerualStyleField> network used for stylization
        :mesh: <mesh> to be stylized
        :renderer: <Renderer> used to take screenshots of the mesh
        :encodings: <tensor> of prompt encodings
        :clip_model: <CLIP> model used for loss calcuation and image embedding
        :optimizer: <torch.optim> used for optimization of the network parameters
        :crop_update: <int> size of crop
        :args: <dict> of arguments passed to execution script
        :i: <dict> testing iteration 
    """
    loss, norm_loss = losses
    rendered_images, elev, azim = renderer(args['n_views'])
    encoded_text, encoded_image, encoded_norm = encodings
    if encoded_text is not None: encoded_input = encoded_text
    elif encoded_image is not None: encoded_input = encoded_image

    # training on augmentations
    if args['n_augs'] == 0: 
        rendered_encodings = clip_model.encode_image(clip_transform(rendered_images))
        if encoded_text is not None: loss = loss_3(rendered_encodings, encoded_input)
        elif encoded_image is not None: loss = loss_2(rendered_encodings, encoded_input)
    else: loss = __test(clip_model, rendered_images, encoded_input, loss, args['n_augs'], aug_transform)
    
    if args['crop_steps'] != 0 and crop_update != 0 and i != 0 and i % args['crop_steps'] == 0:
        crop_cur += crop_update
        _normaug_transform = normaug_transform(crop_cur)
    else:
        if args['crop_forward'] : crop_cur = args['norm_min_crop']
        else: crop_cur = args['norm_max_crop']
        _normaug_transform = normaug_transform(crop_cur)
    
    if args['split_norm_loss']: _require_grad(nsf.normals, False) 
    loss.backward(retain_graph = True)

    # training on norm augmentations
    if args['n_normaugs'] > 0: 
        if encoded_text is not None: 
            encoded_input = encoded_text
            weights = norm_weight

        elif encoded_image is not None: 
            encoded_input = encoded_image
            weights = 1.0

        norm_loss = __test(clip_model, rendered_images, encoded_input, norm_loss, args['n_normaugs'], _normaug_transform, weights)

        if args['split_norm_loss']: _require_grad(nsf.normals, True) 
        if args['split_color_loss']: _require_grad(nsf.colors, False) 
        if args['no_prompt']: norm_loss.backward(retain_graph = True)

    # training on displacement augmentations
    if args['geoloss']:
        default_color = _create_color(len(mesh.vertices), [0.5]*3)
        mesh.face_attributes = kal.ops.mesh.index_vertices_by_faces(default_color.unsqueeze(0), mesh.faces)
        georendered_images, elev, azim = renderer(args['n_views'])

        if args['n_normaugs'] > 0: 
            geo_transform = displaug_transform(args['norm_min_crop'])
            norm_loss = __test(clip_model, georendered_images, encoded_norm, norm_loss, args['n_normaugs'], geo_transform)
            if encoded_image is not None: loss = __test(clip_model, georendered_images, encoded_image, loss, args['n_normaugs'], geo_transform)

        norm_loss.backward(retain_graph=True)
    optimizer.step()

    for layer in [nsf.normals, nsf.colors]: _require_grad(layer, True)

    return rendered_images, loss, norm_loss

### Helper Functions ###
def _require_grad(layer, true): 
    """Sets the truth of all parameters of a layer require grad"""
    for param in layer.parameters(): param.requires_grad = true

def _create_color(n, color_list):
    """Constructs a color tensor"""
    color = torch.zeros(n, 3).to(device)
    color[:, :] = torch.tensor(color_list).to(device)
    return color

def __test(clip_model, rendered_images, encoded_input, loss, n_augs, transform, weight = 1.0):
    """
    Calculating loss of the rendered images using clip embeddings

    Inputs
        :clip_model: <CLIP> model for image embedding generation
        :rendered_images: <tensor> of rendered images of the mesh
        :encoded_input: <tensor> clip embedding of image or text prompt
        :loss: <tensor> loss of the neural style field
        :n_augs: <int> number of augmentations 
        :transform: <tensor> of transformation to apply to rendered images
        :weight: <float> weight to scale loss by
    """
    rendered_encodings = clip_model.encode_image(transform(rendered_images))
    for _ in range(n_augs):
        if encoded_input.shape[0] > 1: loss -= weight * loss_1(rendered_encodings, encoded_input)
        else: loss -= weight * loss_2(rendered_encodings, encoded_input)
    return loss
