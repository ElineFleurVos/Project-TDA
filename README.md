# Project Description
The project consists of a C# visualization and a Python mapper implementation. 
The C# project build process is self-explanatory. The Python mapper project can be built as follows:

## Build

The project uses Python 3.10 but should work on different Python versions. The following packages are required:
- pygame
- networkx
- disjoint-set

The trajectory files are not included in the repository due to their size. To use the program, extract all trajectory data into a 'Data' folder within this directory. The program will find all `.plt` files in the 'Data' directory recursively.  

To run the program, execute the 'App.py' file.

## Settings

Many variables are placed in the 'settings.py' file, which can be modified according to your preferences. The variable names should be self-explanatory.

## Controls

The following controls are available:
- WASD keys: Camera movement
- [O]: Next timeslot
- [P]: Previous timeslot
- [1]: Point clouds (all)
- [2]: Point clouds by timeslot
- [3]: Alpha simplex per timeslot
- [4]: Alpha simplex connected components
- [5]: Graph points overlaid on the map
- [6]: Draw edges
- [7]: Split view
- [8]: Kumaii graph positions
- [9]: Graph density
