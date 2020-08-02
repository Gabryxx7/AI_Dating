import dash
import sys
import threading
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly
import pandas as pd
import nltk
from random import random

class MessageDashboard:
    def __init__(self, messages=None):
        self.data = [
            {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
            {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
        ]

        self.layout = {
            'title': 'Messages Quick Analysis'
        }
        self.classifier = None
        self.train_model()

        self.app = dash.Dash()
        self.app.layout = html.Div(children=[
            html.H1(children='Tinder AI'),

            html.Div(children='''
                    Messages Quick Analysis
                '''),

            dcc.Graph(
                id='example-graph',
                figure={
                    'data': self.data,
                    'layout': self.layout
                },
                animate=True)
        ])

        self.app.callback(dash.dependencies.Output('example-graph', 'figure'),
                     [])(self.update_messages)
        threading.Thread(target=self.run_dash, daemon=True).start()

    def run_dash(self):
        self.app.run_server(debug=False)

    def extract_features(self, message):
        features = {}
        for word in nltk.word_tokenize(message):
            features['contains({})'.format(word.lower())] = True
        return features

    def train_model(self):
        posts = nltk.corpus.nps_chat.xml_posts()
        fposts = [(self.extract_features(p.text), p.get('class')) for p in posts]
        test_size = int(len(fposts) * 0.1)
        train_set, test_set = fposts[test_size:], fposts[:test_size]
        self.classifier = nltk.NaiveBayesClassifier.train(train_set)

    def extract_sender_features(self, message, sender_id):
        if message['from'] == sender_id:
            return self.extract_features(message['message'])

    def update_messages(self, messages, sender_id):
        # fmessages = [(self.extract_features(m['message']), m.get('class')) for m in messages]
        # for m in messages:
            # print(self.classifier.classify(m['message']))
        sent_msgs = list(filter(lambda m: m['from'] == sender_id, messages))
        received_msgs = list(filter(lambda m: m['from'] != sender_id, messages))
        f_sent_messages = list(map(lambda m: self.classifier.classify(self.extract_features(m['message'])), sent_msgs))
        f_received_messages = list(map(lambda m: self.classifier.classify(self.extract_features(m['message'])), received_msgs))

        traces = list()
        for fl in [f_sent_messages, f_received_messages]:
            df = pd.DataFrame(fl, columns=['class'])
            traces.append(plotly.graph_objs.Bar(
                x=df,
                name='Histogram'
            ))
            layout = plotly.graph_objs.Layout(
                barmode='relative'
            )
        print(f_received_messages)
        return {'data': traces, 'layout': layout}