# from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
# from rasa.shared.nlu.training_data.training_data
from rasa.shared.nlu.training_data.formats.rasa_yaml import RasaYAMLReader
filepresent = RasaYAMLReader.is_yaml_nlu_file("../data/nlu.yml")
if(filepresent):
    print('Yes file is present')
    ymlReader = RasaYAMLReader()
    data = TrainingData()
    data = ymlReader.read("../data/nlu.yml")
    print('printing file')
    print(data.intents)
