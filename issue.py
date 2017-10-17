import json
import click
import requests
import re
import arrow


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
        self.issue_url = "https://github.com/EtherTW/talks/issues/{0}".format(_id)
        self.content = requests.get(url).json()
        self.title = self.content["title"]
        self.body = self.content["body"]
        for chunk in self.body.split("### ")[1:]:
            if chunk.startswith('Abstract'):
                self.abstract = chunk.split('\n', 1)[1].rstrip()
            elif chunk.startswith('Language'):
                self.language = self.extract_language(chunk)
        self.speaker = self.content['user']['login']
        self.time = 40  # minutes #TODO: get this info from issue

    @staticmethod
    def extract_language(string):
        regex = r"- \[x\] (.*)\n"
        matches = re.finditer(regex, string)
        return next(matches).group(1)

    def talk_info(self):
        return "{title}\n\nby {speaker}\n\n{abstract}\n\nLanguage: {language}\n\n{issue_url}".format(**self.__dict__)


class Event:
    def __init__(self, path):
        self.content = read_json(path)
        self.event_id = self.content["event"].split("/")[-1]
        self.issues = [Issue(_id=talk["issue"])
                       for talk in self.content["talks"]]

    def show_event(self):

        agenda = Agenda(start=arrow.utcnow().replace(
            hour=19, minute=0, second=0))
        agenda.add_item("Networking", 30)

        for issue in self.issues:
            print(issue.talk_info())
            agenda.add_item(issue.title, issue.time)
            agenda.add_item("Break", 10)
            print("\n\n")
        print("\n\n")
        print(agenda.show_agenda())


class Agenda:
    def __init__(self, start):
        self.agenda = []
        self.start = start

    def add_item(self, title, minutes):
        self.agenda.append([title, minutes])

    def show_agenda(self):
        output = "Agenda\n\n"
        current_time = self.start
        for title, minutes in self.agenda:
            moments_later = current_time.shift(minutes=+ minutes)
            output += "{0} - {1}\t {2}\n".format(
                current_time.format("HH:mm"), moments_later.format("HH:mm"), title)
            current_time = moments_later
        return output


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
@click.argument('path')
def show(path):
    event = Event(path)
    print(event.show_event())


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
