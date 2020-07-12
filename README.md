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
1. **Converts non standard MIDI files into standard MIDI.** <br>This can be useful to generate data from loop packs. Usually, you can find loops for Kick, Snare or Hi-Hats but they're usually given on a single note pattern that not follow the drums MIDI standard.<br> For example, a Hi-Hat loop could be written on a D2 note. <br>Our code automatically translates your file into a standardized one, all you have to do is to rename your file with the name of the element in it. If you have a Kick loop, just rename it like *"Kick_01"*, if you have a Hi-Hat loop, just rename it like *"Hi_Hat_01"* and so on.  
2. **Generates artificial loops**. <br>The code combines Kick, Snare and Hi-Hats loops in order to generate new artificial drums loops, created by randomly combining patterns of Kick+Snare+Hi-Hat. This approach has been inspired by the typical **Data Augmentation** process used in **Image Classification**, we will discuss this process in the [Results](#Results) part. 

## Data Pre-Processing
We need to convert our MIDI input data into a appropriate format for our Neural Network. <br> First thing first, we will convert our MIDI file into a *.txt* file. Then we're going to encode all the notes with the following scheme:

![Model diagram](https://keunwoochoi.files.wordpress.com/2016/02/screen-shot-2016-02-23-at-10-52-12.png?w=1200)

We're going to represent this scheme in a *.txt* format using *binary numbers*. Here's an example:
```
‘000000000’ : nothing played <br>
‘100000000’ : kick is played <br>
‘1000000001’ : kick and crash played <br>
‘0101000000’ : snare and open-HH played
```
Each one of the above 9-bit numbers represents the elements of my drumkit which has been played at that given moment. <br>
We're quantizing our MIDI input with *16-th notes* (you can easily change it inside the code, you can also set 32-th notes and try to experiment). <br>Our converted MIDI file will look something like:
```
0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 BAR 
0b010000000 0b010000000 0b000000000 0b010000000 0b010000000 0b000001000 0b000000000 0b000001000 0b010000000 0b000000000 0b000000000 0b000001000 0b000000000 0b000001000 0b000001000 0b000000000 BAR 
```
As you might notice, we have a **BAR** element every 16 notes, which denotes the end of a **music measure**. 

In the specific case of Trap Music, we suggest a **32-th note resolution** in order to represent the Hi-Hat "high speed" repetitions. Notice that this will double up the dimension of the input txt with all the realated consequences (longer training time ecc...) <br>
We stuck to *16-th notes* to simplify the process. 

## Model training
For our task we selected a standard **LSTM Neural Network**. <br>Our network is based on the well known model for *text prediction*, you can find an example here: https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb

In particular we used the following network:
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
Then we tested and tuned different values for the parameters (such as *layer size*, *number of layers* ecc...). <br> ```maxlen``` is the length of the input, we noticed that the best values for ```maxlen``` are **256, 512, 1024**. <br>
You have to tune this parameter according to your input encoding. For example a ```maxlen``` value of **256** with *16-th notes* resolution, corresponds to an input size of **16 musical measures**, while in the case of *32-th notes* corresponds to **8 measures**. 

For further considerations/explanations on our model and testing, go to the [Results](#Results) section. The model provided here is the "standard" one, the same used in the paper and in many text prediction tasks. 

## Model Prediction 
Once the model has been trained, we can use it to generate new data.<br> As shown in the **txt LSTM** (https://github.com/fchollet/deep-learning-with-python-notebooks/blob/master/8.1-text-generation-with-lstm.ipynb) we extract a random sequence from our training dataset and then we use it as a starting point for our prediction. <br>Our model will continue the sequence with its own generated data.

A very important function is the following one:
```
def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)
```
This function exploits the well known paradigma of **exploration vs exploitation** used in **Reinforcement Learning**. The main idea is to allow exploration at prediction time.
<br>Instead of always taking the prediction that maximizes the output probability, we slightly randomize the output process to encourage exploration and new patterns. <br>High values of ```temperature``` increase the probability of occasional events (so exploration), while low values of ```temperature``` discourage occasional events (exploitation). 

## Model Post-Processing
Our model will generate a *.txt file* as output, containing its prediction. Since we're interested in generating useful loops, we have to convert our *.txt file* into a MIDI file.
The process is the same as the [Pre-Processing](#Data-Pre-Processing) part but in reverse order. <br> So we will extract MIDI notes from their *.txt* representation. 

# Results
Did we end up with a good drums generator? Unfortunately, not at all.  <br>We're going to make a deeper analysis of why we failed and how to solve the problem. <br>
Here's an example of our prediction: Link here.

## Emulating the original paper results
We were able to correctly emulate the results provided in the paper + blog post. <br>
Data pre-processing and post-processing functions work perfectly, they have been tested multiple times and show coherent results.

Then we trained our model over the **Metallica dataset** for **60 epochs**, and we obtained coherent results. After 60 epochs of training our model has learnt the *16 notes bar structure*, we were able to obtain the same result of the paper. <br> Here's an example of our predicted output in this case: 
```
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b100000001 0b000000000 0b110000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b110000000 0b000000000 0b000000000 0b000000000 0b111000001 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b100000001 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
BAR 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 0b000000000 
```
Here's the output provided by the author of the paper:
![Model diagram](https://keunwoochoi.files.wordpress.com/2016/02/screen-shot-2016-02-23-at-11-28-06.png?w=1200)

As you might notice, both networks have learnt the *16 note bar* pattern! 

Our network has a quite sparse prediction (predicts mostly ```0b000000000```) because in this case, we used a simpler model than the one proposed (faster to train). The goal was to test and demonstrate that the network was capable of learning repeating patterns.

## Addressing the problem

The previous results give us some certainties: we know that our model is capable of learning patterns, behaves coherently with the input data and we do not have strange bugs.
Unfortunately, our prediction on our trap dataset is still pretty poor.

Knowing this, we started investigating the cause of the problem. 

We first started by testing and tuning the network parameters.<br> We changed the number of layers, neurons per layer, sequence length, epochs ecc... but our model never learnt something meaningful. We had the best results with ```max_len = 256```, *2 layers* and *1024 neuron per layer*.

Our model outputs ```BAR``` every 7-8 notes (with some exceptions), which shows some kind of learnt pattern on ```BAR```.<br> All the other models failed at capturing this behavior: they never predicted any BAR or they placed ```BAR``` totally random. Here's an example of the output:

```
BAR 0b101000000 0b000000000 0b000000000 0b101000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b101000000 0b001000000 0b001000000 0b000000000 0b000000000 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b001000000 0b001000000 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b101000000 0b001000000 0b001000000 0b001000000 
BAR 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b101000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 
BAR 0b101000000 0b000000000 0b000000000 0b001000000 0b001000000 0b001000000 0b001000000 
BAR 0b101000000 0b000000000 0b000000000 0b001000000 0b001000000 0b000000000 0b000000000 
```

Then we decided to plot the training behavior of our network on the Metallica dataset:

![Model diagram](https://i.imgur.com/y2rq0RU.png)


Which shows the typical behavior of a network that, at a certain point, starts overfitting. 
So we decided to check the training behavior of the model on our dataset, since the really poor performances, we supposed that our model could be overfitting or underfitting the data.
This is a couple of results we got with different models (changing some hyperparameters):

![Model diagram](https://i.imgur.com/fOAzcG7.png)
![Model diagram](https://i.imgur.com/effP0e4.png)
![Model diagram](https://i.imgur.com/HSPgeeS.png)
![Model diagram](https://i.imgur.com/vEkLP3X.png)

Looking at the previous charts seems that our model is perfect! 
1. No underfitting -> Training loss converges to 0
2. No overfitting -> Validation error constantly follows the Training error

But the previous graphs are misleading. The last 2 plots are particularly interesting since give us a hint about the real problem, we will discuss it in the following section.

## Poor dataset

In the previous part we discussed how we tested our model and we were able to reproduce the behavior of the scientific paper. This shows us that our model is correct (in general) and is capable of learning patterns. So why is it failing in our case?

First thing first the metallica dataset has 23150 training sequences, while our dataset has only about 8000 training sequences, which is only a third of the data! But this is not the only problem.

As we mentioned in the Data input/generation section, our dataset has been built by combining a "pool" of Kick/Snar/Hi-Hats loops. This pool has been created using free samples pack and contains roughly 20 indipendent samples. 
We generated 530 two bar long samples combining the above mentioned Kick/Snare/Hi-Hat loops together. 

This means that basically, given the low amount of original samples and the high amount of generated data, our dataset will surely contain multiple copies of the same identical loop! <br> This is clearly shown by the last 2 plot of the loss: the validation loss follows almost exactly the training loss because the validation set contains basically the same data of the training set!

Also another problem is that the Metallica dataset contains full real songs, which surely helps in the training phase, while our dataset contains only artificial loops (no real complete song).

It is worth noting that the generation approach is pretty interesting and could open new interesting field in the research of RNN. <br> The basic idea is to emulate the Data Augmentation used in Image Classification, given a proper training set, could be a good idea to generate new artificial samples by combining piece of the original dataset together. This seems a possible good idea, especially in the case of drums (could be a bad idea in text generation, since you will likely generate total random sentences).

The metallica dataset has 23150 training sequences, while our dataset has only about 8000 training sequences.

# Conclusions
Unfortunately we were not able to create a proper working application due to the lack of free data and free resources. MIDI for trap songs can be found on the internet, but unfortunately there are no free legal resources. 

Given a proper amount of good data, our model will likely work with a bit of tuning. 
