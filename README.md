# TrapGenerator
This project focuses on the automatic drum generation for trap music. Our goal is to create a model capable of creating drums loop for trap music.
<br>The whole project is based on the following paper: https://arxiv.org/pdf/1604.05358v1.pdf


## Project overview
The project can be modeled by the following diagram:


![Model diagram](https://i.imgur.com/BtYp4Sr.png)


We used the following libraries: 
1. **MIDI processing**: https://github.com/jameswenzel/mydy
2. **Neural network model**: https://www.tensorflow.org/


## Data Input/Generation
We use standard MIDI files as input data.<br> **Input data must follow the standard MIDI drums representation:** https://www.zendrum.com/resource-site/drumnotes.htm <br>

So for example, the Kick should be placed on note 35/36 of the MIDI roll (which is mapped to a C0 or C1 note, depending on your DAW, we discovered that Ableton has a different representation of notes with respect to Reaper, for example).

We decided to use this standard in order to exploit the majority of MIDI files you can find on the internet. 

So, for example, you can download your files from here: https://www.supreme-network.com/midis/browse/P/1667-post-malone/8542-rockstar or here: http://en.midimelody.ru/lamb-of-god/ and just use them without any further processing.  

We also wrote some code (...) which performs 2 important tasks:
1. **Converts non standard MIDI files into standard MIDI.** <br>This can be useful to generate data from loop packs. Usually, you can find loops for Kick, Snare or Hi-Hats but they're usually given on a single note pattern that not follow the drums MIDI standard.<br> For example, a Hi-Hat loop could be written on a D2 note. <br>Our code automatically translates your file into a standardized one, all you have to do is to rename your file with the name of the element in it. If you have a Kick loop, just rename it like "Kick_01", if you have a Hi-Hat loop, just rename it like "Hi_Hat_01" and so on.  
2. **Generates artificial loops**. <br>The code combines Kick,Snare and Hi-Hats loops in order to generate new artificial drums loops, creating by randomly combining patterns of Kick+Snare+Hi-Hats. This approach has been inspired by the typical Data Augmentation process used in Image Classification, we will discuss this process in the Results part. 

## Data Pre-Processing
We need to convert our MIDI input data into a suited format for our Neural Network. First thing first, we will convert our MIDI file into a txt file. Then we're going to encode all the notes with the following scheme:

![Model diagram](https://keunwoochoi.files.wordpress.com/2016/02/screen-shot-2016-02-23-at-10-52-12.png?w=1200)

We're going to represent this scheme in a txt format using binary numbers. Here's an example:

‘000000000’ : nothing played <br>
‘100000000’ : kick is played <br>
‘1000000001’ : kick and crash played <br>
‘0101000000’ : snare and open-HH played

Each one of the above 9bit number represents the elements of my drumkit which have been played at that given moment. <br>
We're quantizing our MIDI input with 16-th notes (you can easily change it inside the code, you can also set 32-th notes and try to experiment), so our converted MIDI file will look something like:

0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 BAR 0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 0b010000000 0b000000000 0b000000000 0b000001000 0b000000000 0b000001000 0b000001000 0b000000000 BAR 

As you might notice, we have a BAR element every 16 notes, which denotes the ending of a musical bar. 

In the specific case of Trap Music, we suggest a 32-th note resolution in order to represent the Hi-Hat "high speed" repetitions. Notice that this will double up the dimension of the input txt with all the realated consequences (longer training time ecc...) <br>
We sticked to 16-th notes to simplify the process. 

## Model training
For our task we selected a standard LSTM Neural Network. Our network is based on the well known model for text prediction, you can find an example here: https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb

In particular we used the following "base" networks:
1. Network 1:
```
model = Sequential()
model.add(LSTM(512, return_sequences=True, input_shape=(maxlen, num_chars)))
model.add(Dropout(0.2))
model.add(LSTM(512, return_sequences=True))
model.add(Dropout(0.2))
model.add(LSTM(512, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(num_chars))
model.add(Activation('softmax'))
 
model.compile(loss='categorical_crossentropy', optimizer='adam')
```
And then we tested and tuned different values for the parameters (such as layer size, number of layers ecc...). <br> maxlen is the length of the input, we noticed that the best values for maxlen are 256, 512, 1024. <br>
You have to tune this parameter according to your input encoding. For example a maxlen value of 256 with 16-th notes resolution, corresponds to an input size of 16 musical bar, while in the case of 32-th notes corresponds to 8 bars. 

For further consideration/explanation on our model and testing, go to the Results section. The model provided here is the "standard" one, the one proposed in the paper (and in many other text prediction tasks)

## Model Prediction 
Once we have trained our model, we can use it to generate new data. As shown in the txt LSTM (https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb) we extract a random sequence from our training dataset and we use it as a starting point for our prediction. Our model will "continue" the sequence with its own generated data.

A very important function is the following:
```
def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)
```
This function exploits the well known paradigma of exploration vs exploitation used in Reinforcement Learning. <br>
The main idea is to allow exploration at prediction time, instead of taking always the prediction that maximizes the output probability, we slightly randomize the output process in order to encourage exloration and new patterns. High values of temperature increases the probability of occasional events (so exploration), while low values of temperature discourage occasional events (exploitation). 

## Model Post-Processing
Our model will generate a txt file as output, containing its prediction. Since we're interested in generating useful loops, we have to convert our txt file into a MIDI file.
The process is the same of the Pre-Processing part, but in reverse order. 
From txt in the already mentioned format, we will extract the corresponding MIDI notes and we will append them in a MIDI file. We're doin this using the above mentioned Python library. 


# Results
Did we end up with a good drums generator? Unfortunately, not at all, but we're going to make a deeper analysis on why we failed and how to solve the problem.
Here's an example of our prediction: Link here.

## Emulating the original paper results
We were able to correctly emulate the results provided in the paper + blog post. <br>
The data pre-processing and post-processing functions work perfectly, they have been tested multiple times (converting from MIDI to txt and then from txt to MIDI we obtained again the original file) and show coherent results.

Then we trained our model over the Metallica dataset for 60 epochs, and we obtained coherent results. In fact, as shown in the blog-post related with the paper. The metallica dataset has 23150 training sequences, while our dataset has only about 8000 training sequences.






































In the Drum Generation folder you find the current code. The Basecode folder containts the basecode i'm using (developer by a researcher), that's the starting point. The jupyter file you find inside the Drum generation folder are some experiment of checking/converting MIDI files.

What we have to do is to take the Basecode code and convert it into a working code: the code is written in Python2 + uses deprecated libraries. I already figure out how to convert the python-midi library (which is used in the original code and available only for python2) into a Python3 compatible library. 

**NB**: Don't run the jupyter notebooks Model Prediction and Model Training together! This will lead to an error caused by the simultaneous use of the GPU by the 2 codes. You have to first run the model training, and get your model_weights file (which contains the parameters of the model), then you close the kernel of the jupyter notebook and then you run the Model Training code. 

**NB2** = Kick goes on C1(Note number 36), Snares goes on D1(Note numer 38)  and hi hat goes on F#1(note number 42). Careful about the note notation. Some sequencers/products refers to MIDI note 36 as C1, others as C0! To be sure about the actual note, use the MIDI number

https://www.supreme-network.com/midis/browse/P/1667-post-malone/8542-rockstar Nice website to build a dataset, unfortunately, you must pay 

Useful resources: https://stackoverflow.com/questions/47125723/keras-lstm-for-text-generation-keeps-repeating-a-line-or-a-sequence 
https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb
