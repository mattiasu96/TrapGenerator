# TrapGenerator
Automatic Trap Music Generator 

In the Drum Generation folder you find the current code. The Basecode folder containts the basecode i'm using (developer by a researcher), that's the starting point. The jupyter file you find inside the Drum generation folder are some experiment of checking/converting MIDI files.

What we have to do is to take the Basecode code and convert it into a working code: the code is written in Python2 + uses deprecated libraries. I already figure out how to convert the python-midi library (which is used in the original code and available only for python2) into a Python3 compatible library. 

**NB**: Don't run the jupyter notebooks Model Prediction and Model Training together! This will lead to an error caused by the simultaneous use of the GPU by the 2 codes. You have to first run the model training, and get your model_weights file (which contains the parameters of the model), then you close the kernel of the jupyter notebook and then you run the Model Training code. 
