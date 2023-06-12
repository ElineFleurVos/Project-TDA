# Build
I am using python 3.10 but should work on different python version. Packages required:
- pygame
- networkx
- disjoint-set

The trajectory files are not included in the repository due to size.
So extract all trajectories data in a 'Data' in this folder. 
The program finds all .plt files in the 'Data' directory recursively.  

Then run the 'App.py' file.

# Settings
Many variables are placed in the 'settings.py' file, which can be modified to your liking. 
Names should be self-explanatory.

# Controls
- WASD keys for camera movement.
- [Q] and [E] to zoom in/out.
- [1] and [2] to increase/decrease the current visualized time slot.
- [C] toggle between split view of simplicies and graph or one view with the graph overlayed.
- [P] toggle between render point cloud or alpha complexes.
- [3] set graph type to 'physics' uses my badly implemented physics to move graph points.
- [4] set graph type to 'map' set points to their connected components position.
- [5] set graph type to 'networkx' using kamada_kawai_layout.
- [O] toggle between showing all points or only current timeslot points.
