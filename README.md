# Beyond 2022
Virtual Archive Chaotbot - 

This project contains a baseline Q&A bot related to the project Beyond 2022 implemented using Rasa framework.
This also contains a code for middleware to implement Wizard Of Oz Experiment.

Following are the details of files and folder having important code - <br>
<b>domain.yml</b> - This file is a part of rasa core which contains the list of intents, entities and corresponding actions.<br>
<b>data</b> - This folder contains the input data including all the utterances for individual intents used for training bot.<br>
<b>middleware</b> - This folder contains python script for WOz middleware. <br>
<b>utils</b> - This folder contains seed data csv and python script used for data cleaning and converting the data into rasa training data format.<br>
<b>ui</b> - This folder contains HTML files for User and Wizard Interface.<br>
<b>paraphraser</b> - This folder contains python script file which implements data cleaning and paraphraser for data augmentation.<br>

