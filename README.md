
# NaoTools

A blender panel to help streamline the model importing/cleanup process for various games. 




## Installation

Install the project like any other blender plugin. Download the .zip then click edit --> preferences 

![h](https://media.discordapp.net/attachments/831687902824103977/1140984522100453386/Screenshot_31.png)

Then go into Add-ons, click install, navigate to the .zip and install it, then enable it.

![h2](https://media.discordapp.net/attachments/831687902824103977/1140984821791862804/Screenshot_32.png)


## Features

![h3](https://media.discordapp.net/attachments/831687902824103977/1140985177120706641/Screenshot_33.png)

NaoTools has 5 core features that just about anyone can make use of for any workflow in regards to importing custom models into games. While these are catered towards the workflow of P5R and Smash model importing, I've personally used it to help expedite the process in Sifu (a UE4 game). 

### Limit Weights
Limit weights limits the amount of vertex groups a vertice can have for it's influence. Most games abide by 4, however there are some exceptions where less are allowed like in some switch games, or an infinite amount is allowed like P5R PS4. Generally, 4 is what you want, however you can customize the amount with a slider below the button, from 1-10. After you do this, it auto normalizes itself, however the Normalize button is there in case you make changes post weight limiting. 

### Normalize Weights
This button is simply to make sure every vertice has a influence count adding up to 1. Blender doesn't auto normalize by default, and not everyone auto normalizes, so this button just does that but after basically. 

### Rename UV Maps 
This button will rename the primary UV Map of every Mesh in the scene to whatever is entered in the box below it. The default is "UV0" which is what P5R uses, however the names of UVMaps that P4D, and Smash Ultimate are listed in the naming guide below it. If you use this tool for another game and want those uv names added, please make a github issue so I can append the list with more games.

### Split by Materials 

When rigging, alot of the time it's a good idea to combine all meshes into one for easier editing of weights, or stealing weights easier. After all this is one advantage Blender has over something like 3ds Max, which murders normals when you split meshes. 

To demonstrate an example, here is a simplified Rise P4D mesh broken down into the 3 textures it uses before clicking the button. 

![h4](https://media.discordapp.net/attachments/831687902824103977/1140987049873264693/Screenshot_34.png?width=1098&height=670)

Notice how the mesh has 3 materials. Well I've already rigged the mesh, and normalized weights, and now I want to split it by all the materials. So I click the button, and then...

![h5](https://media.discordapp.net/attachments/831687902824103977/1140987049550282824/Screenshot_35.png?width=1034&height=670)

Now it's split the mesh by material, and cleaned up the non used materials from the split meshes! 

### Triangulate Faces
This button will triangulate the selected mesh, I personally like to turn meshes into quads so they're easier to edit. So a button like this helps my workflow out a bit and saves a second of going into edit mode and pressing f3 to search. This can also help if you've made a custom model and need to triangulate it. 
