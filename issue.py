import json
import click
import requests
import re


def read_json(path):
    with open(path) as f:
        json_dict = json.load(f)
    return json_dict


def write_json(path, _dict):
    with open(path, "w") as f:
        f.write(json.dumps(_dict))


class Issue:
    def __init__(self, _id):
        url = "https://api.github.com/repos/EtherTW/talks/issues/{0}".format(
            _id)
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
        self.event_id = self.content["event"].split("/")[-1]
        issues = []
        for talk in self.content["talks"]:
            issue = Issue(_id=talk["issue"])
            print(issue.talk_info())
            issues.append(issue)
        self.issues = issues


class MeetupAPI:
    def __init__(self):
        # Get one from https://secure.meetup.com/meetup_api/key/
        with open('.api_key', 'r') as f:
            self.key = f.readlines()[0]
        self.host = "api.meetup.com"
        self.urlname = "Taipei-Ethereum-Meetup"

    def get_event_info(self, event_id):
        url = "https://{0}/{1}/events/{2}".format(
            self.host, self.urlname, event_id)
        response = requests.get(url, params={"sign": "true"})
        return response.json()


@click.group()
def cli():
    pass


@cli.command()
@click.option('--path', help='path of meetup event config')
def show_event(path):
    event = Event(path)


@cli.command()
@click.argument('title')
def new(title):
    default = {
        "event": "",
        "talks": []
    }
    write_json("./meetups/{0}.json".format(title), default)

    click.echo("Create a new meetup at {0}".format(title))


if __name__ == '__main__':
    cli()
