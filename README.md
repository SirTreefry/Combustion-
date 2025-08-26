# Combustion-
Custom Combustion Codes for JAS at UCF inline jet engine

# Combustion-
The two must updated scripts that should be used is combustor4.py. Combustor3.py is a good setup for the design and setup and the paper for this jet engine
can be found here -> https://www.mdpi.com/2226-4310/11/1/22

The geometry and air mass flow are the most important editable variables present in the code that physcially effect the shape of the combustor.

The Gaussian Pulse Code can be edited and is found here -> https://cantera.org/3.1/examples/cxx/combustor.html

Installation Guide for Python
==========================================
Cantera
install conda

conda create --name cantera-env python=3.10


conda activate cantera-env

pip install cantera matplotlib ipykernel

python -m ipykernel install --user --name cantera-env --display-name "Python (cantera-env)"

Go to anaconda and load spyder
-Go to tool -> Preferences -> Python interpreter
C:\Users\<your-username>\anaconda3\envs\cantera-env\python.exe

if your spyder doesn't have a kernel
reload cantera environment
conda activate cantera-env
pip install spyder-kernels==2.5.*

