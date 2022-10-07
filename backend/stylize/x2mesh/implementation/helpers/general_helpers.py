import os
import requests
import mimetypes
from os import listdir
from ..utils import check_mesh
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
from os.path import isfile, join, isdir

def get_valid_models(dir_path, models = {}, text2mesh_path = "../text2mesh"):
    """
    Fetches all the available models in the directory given

    Inputs
        :dir_path: <str> to the directory containing model directories and model files
    
    Outputs
        <dict> from model name to model path
    """
    for filename in listdir(dir_path):
        file_path = f"{dir_path}/{filename}"
        if isfile(file_path):
            if ".obj" == filename[-4:]:
                try: 
                    check_mesh(file_path)
                    models[filename[:-4]] = file_path
                except ValueError: print(f"\033[91mFail[{file_path} Deprecated]\033[0m")
                
        elif isdir(file_path):
            models = get_valid_models(file_path, models, text2mesh_path)
    print(f"Found {len(models)} working models in {dir_path}")
    return models

def select_model(models: dict, selected_model = None):
    """
    Helps user know which models are available and select which one to use

    Inputs
        :models: <dict> of model name to path

    Outputs
        <str> path to selected model
    """
    print(f"The available models are:\n{list(models.keys())}")
    if selected_model is None: selected_model = input("Name of model you want to use: ")
    return selected_model, models[selected_model]

def display(pathes):
    """
    Displays the first and last iteration
    
    Inputs
        :pathes: <list> of pathes to images to show
    """
    n = len(pathes)
    f, plot = plt.subplots(n, 1, figsize=(12, 5))
    for i in range(len(pathes)):
        image = mpimg.imread(pathes[i])
        plot[i].imshow(image)
    plt.show()

def download(home_dir, url = None, stream = False, fn = None):
    """
    Downloads the content of a url to the specified home_dir

    Inputs
        :url: <str> to the location contianing the content
        :home_dir: <str> the home directory containing subdirectories to write to
        :fn: the name to give the file when saved
    
    Outputs
        :returns: the path to the saved file containing the content
    """
    if url is None:
        url = input("Image url: ")
        
    if fn is None:
        fn = url.split('/')[-1]

    r = requests.get(url, stream=stream)
    if r.status_code == 200:
        content_type = r.headers['content-type']
        ext = mimetypes.guess_extension(content_type)
        with open(f"{home_dir}/outputs/{fn}{ext}", 'wb') as output_file:
            if stream:
                for chunk in r.iter_content(chunk_size=1024**2): 
                    if chunk: output_file.write(chunk)
            else:
                output_file.write(r.content)
                print("{} downloaded: {:.2f} KB".format(fn, len(r.content) / 1024.0))
            return f"{home_dir}/outputs/{fn}{ext}"
    else:
        raise ValueError(f"url not found: {url}")