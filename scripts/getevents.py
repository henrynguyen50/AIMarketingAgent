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
        event = data['events'][0]['strEvent']
        date = data['events'][0]['dateEventLocal']
        name = data['events'][0]['strLeague']

        #needed for wrestlign since matches are not events, matches are given in events description
        description = data['events'][0]['strDescriptionEN']
        f.write(f"\nEvent: {name}" + f" {event}" + f" {date}")
        if description:
             f.write(f"\nCard: {description}")
        
        remove_blank_lines(filepath)
    thumb = data['events'][0]['strThumb']
    name = data['events'][0]['strLeague']
    #download image using binary
    if thumb:
        img_data = requests.get(thumb).content
        with open(f'{name}.jpg', 'wb') as handler:
            handler.write(img_data)

def remove_blank_lines(file):
    file = Path(file)
    lines = file.read_text().splitlines()
    filtered = [
        line
        for line in lines
        if line.strip()
    ]
    file.write_text('\n'.join(filtered))
        
event_ids = [4444, 4563, 4449, 5293, 4424, 4391, 4387]
events_file_path = "scripts/sportsevents.txt"
if __name__ == "__main__":

    lookup_events(event_ids, events_file_path)

