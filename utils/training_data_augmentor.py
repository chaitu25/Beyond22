from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
# from rasa.shared.nlu.training_data.training_data
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader,RasaYAMLWriter
import os
import argparse

filepresent = RasaYAMLReader.is_yaml_nlu_file("nlu.yml")
complete_td = TrainingData()
if(filepresent):
    print('Yes file is present')
    ymlReader = RasaYAMLReader()
    #data = TrainingData()
    complete_td = ymlReader.read("nlu.yml")
    print('printing file')
    print(complete_td)
    l = complete_td.intent_examples
    for m in l:
        print(m.get_full_intent())
        temp = m.as_dict_nlu()
        for k,v in temp.items():
            print(k,v)


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
            print(intent)
            utterance = data[1].strip("\n")
            traingData.setdefault(intent,[]).append(utterance)
    
    print('printing value from dict')
    all_messages = []
    newData = TrainingData()
    for k,v in traingData.items():
        print(k,'->>>',v)
        for ut in v:
            all_messages.append(Message.build(text=ut,intent=k))
    
    complete_td = complete_td.merge(TrainingData(training_examples=all_messages))
    writer = RasaYAMLWriter()
    print('Writing data to nlu file')
    writer.dump("nlu.yml",complete_td)
    print('Writing data to nlu file complete')