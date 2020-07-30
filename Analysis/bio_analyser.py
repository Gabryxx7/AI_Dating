from nltk.classify import NaiveBayesClassifier
from nltk.corpus import subjectivity
from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from API.tinder_api_extended import TinderApi
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.graph_objs as go
import os
import json
from pathlib import Path

class BioAnalyser:
    def __init__(self, tinder_api=None, data_file= None, update_file=False):
        self.tinder_api = tinder_api
        data = None
        with open(data_file, "r") as df:
            data = json.load(df)
        # self.getTinderBios(data)
        nltk.download('vader_lexicon')
        sid = SentimentIntensityAnalyzer()
        if data:
            for profile in data:
                person, type = self.tinder_api.get_person_data(profile)
                if 'bio' in person:
                    ss = sid.polarity_scores(person['bio'])
                    person['bio_sentiments'] = ss
                    if ss['neg'] > 0.5:
                        print("\nBIO: " +person['bio'])
                        print(ss)
                    elif ss['pos'] > 0.5:
                        print("\nBIO: " +person['bio'])
                        print(ss)

            # filename = Path(data_file).stem
            # with open(filename+"_features.json", "w") as df:
            print("Writing file: " +str(os.path.abspath(data_file)))
            if update_file:
                with open(data_file, "w") as df:
                    json.dump(data, df)

    def getTinderBios(self, data):
        for profile in data:
            person, type = self.tinder_api.get_person_data(profile)
            if 'bio' in person:
                self.bios.append(person['bio'])


if __name__ == '__main__':
    data_folder = "../Data/"
    recommendations_folder = data_folder + "recommendations/"
    recommendations_file = data_folder + "recommendations.json"
    matches_folder = data_folder + "matches/"
    matches_file = data_folder + "matches.json"
    profile_folder = data_folder + "profile/"
    profile_file = data_folder + "profile.json"
    tinder_api = TinderApi(data_folder)
    # try:
    #     with open(matches_file, "r") as mf:
    #         matches = json.load(mf)
    #     with open(recommendations_file, "r") as rf:
    #         recs = json.load(rf)
    # except Exception as e:
    #     print("Exception " +str(e))

    bio_analyser = BioAnalyser(tinder_api, data_file=matches_file)
    bio_analyser = BioAnalyser(tinder_api, data_file=recommendations_file)