import json
import click
import requests
import re


def read_json(path):
    with open(path) as f:
        json_dict = json.load(f)
    return json_dict


class Issue:
    def __init__(self, _id):
        url = "https://api.github.com/repos/EtherTW/talks/issues/{0}".format(_id)
        self.content = requests.get(url).json()
        self.title = self.content["title"]
        self.body = self.content["body"]
        for chunk in self.body.split("### ")[1:]:
            if chunk.startswith('Abstract'):
                self.abstract = chunk.split('\n', 1)[1].rstrip()
            elif chunk.startswith('Language'):
                self.language = self.extract_language(chunk)
        self.speaker = self.content['user']['login']

    @staticmethod
    def extract_language(string):
        regex = r"- \[x\] (.*)\n"
        matches = re.finditer(regex, string)
        return next(matches).group(1)

    def talk_info(self):
        return "{title}\nby {speaker}\n{abstract}\nLanguage: {language}".format(**self.__dict__)

class Event:
    def __init__(self, path):
        self.content = read_json(path)
        issues = []
        for talk in self.content["talks"]:
            issue = Issue(_id = talk["issue"])
            print(issue.talk_info())
            issues.append(issue)
        self.issues = issues

@click.command()
@click.option('--path', help='Number of greetings.')
def show_event(path):
    event = Event(path)
    
    print(event.content)






if __name__ == '__main__':
    show_event()
