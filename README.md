# TrapGenerator
This project focuses on the automatic drum generation for trap music.
The whole project is based on the following paper: https://arxiv.org/pdf/1604.05358v1.pdf


## Project overview
The whole project can be represented by the following diagram:






In the Drum Generation folder you find the current code. The Basecode folder containts the basecode i'm using (developer by a researcher), that's the starting point. The jupyter file you find inside the Drum generation folder are some experiment of checking/converting MIDI files.

What we have to do is to take the Basecode code and convert it into a working code: the code is written in Python2 + uses deprecated libraries. I already figure out how to convert the python-midi library (which is used in the original code and available only for python2) into a Python3 compatible library. 

**NB**: Don't run the jupyter notebooks Model Prediction and Model Training together! This will lead to an error caused by the simultaneous use of the GPU by the 2 codes. You have to first run the model training, and get your model_weights file (which contains the parameters of the model), then you close the kernel of the jupyter notebook and then you run the Model Training code. 

**NB2** = Kick goes on C1(Note number 36), Snares goes on D1(Note numer 38)  and hi hat goes on F#1(note number 42). Careful about the note notation. Some sequencers/products refers to MIDI note 36 as C1, others as C0! To be sure about the actual note, use the MIDI number

https://www.supreme-network.com/midis/browse/P/1667-post-malone/8542-rockstar Nice website to build a dataset, unfortunately, you must pay 

Useful resources: https://stackoverflow.com/questions/47125723/keras-lstm-for-text-generation-keeps-repeating-a-line-or-a-sequence 
https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb
