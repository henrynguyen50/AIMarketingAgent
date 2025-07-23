import requests, os
from pathlib import Path

def lookup_events(event_ids, filepath):
    for event in event_ids:
        res = requests.get((f"https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id={event}"))
        if not res:
            continue

        data = res.json()

        if not data.get('events'):
            res = requests.get((f"https://www.thesportsdb.com/api/v1/json/123/eventspastleague.php?id={event}"))
            if not res:
                continue
            data = res.json()
            print_event(data, filepath)
        else:
            print_event(data, filepath)
    

def print_event(data, filepath):
    with open(filepath, "a") as f:
        event = data['events'][0]['strFilename']
        #needed for wrestlign since matches are not events, matches are given in events description
        description = data['events'][0]['strDescriptionEN']
        f.write(f"\nEvent: {event}")
        if description:
            f.write(f"Card: {description}")
        remove_blank_lines(filepath)

def remove_blank_lines(file):
    file = Path(file)
    lines = file.read_text().splitlines()
    filtered = [
        line
        for line in lines
        if line.strip()
    ]
    file.write_text('\n'.join(filtered))
        



