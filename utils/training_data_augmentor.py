from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
# from rasa.shared.nlu.training_data.training_data
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
import os
import argparse

filepresent = RasaYAMLReader.is_yaml_nlu_file("../data/nlu.yml")
if(filepresent):
    print('Yes file is present')
    ymlReader = RasaYAMLReader()
    data = TrainingData()
    data = ymlReader.read("../data/nlu.yml")
    print('printing file')
    print(data.intents)



if __name__ == "__main__":
    filename = ''
    traingData = dict()
    parser = argparse.ArgumentParser()
    parser.add_argument('--fileName',type=str)
    args = parser.parse_args()
    if args.fileName is None:
        filename = 'trainingData.txt'
    else:
        filename = args.fileName
    with open(filename,'r') as file:
        for line in file:
            data = line.split(' ',1)
            intent = data[0]
            utterance = data[1]
            traingData[utterance] = intent
    
    print('printing value from dict')
    for k,v in traingData.items():
        print(k,'->>>',v)
