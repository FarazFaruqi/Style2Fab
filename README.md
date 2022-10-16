# Functionally Aware 3D Manifold Stylization
Official repository for the Functionality-Aware Styling: Fabricating Functional Objects with Selective Stylization paper

#### Abstract
Recent advances in 3D manipulation techniques have led to development of novel interfaces that reduce the effort required to modify 3D models. However, these methods typically perform a global manipulation of the geometry, which can lead to loss of functionality in the 3D models, preventing their usage in domains such as fabrication. In this paper, we introduce a method that selectively modifies parts of 3D models while preserving their overall functionality. We present a novel system that lets users stylize their 3D models using multiple modalities, including images and text. Our method uses differentiable rendering to stylize models, while preserving the functional segments of the 3D model. In this paper, we present the design of the system, along with a technical evaluation of the classification algorithm on popular models from Thingiverse, and present results from a user evaluation of the interface.

#### Installing
````
cd && git clone https://github.com/ATKatary/fa3ds.git 
````

#### Starting backend
````
cd ~/fa3ds && bash start.sh
````

#### Using blender plugin
First install the plugin
```
cd ~/fa3ds/plugin && bash deploy.sh
```
Now open up blender and start using fa3ds!
