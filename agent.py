from models.encode import *
from scripts.getevents import *
from tweet import *
from update_embeddings import *
import time
#get events
#then encode events
#then run tweet.py 

event_ids = [4444, 4563, 4449, 5293, 4424, 4391, 4387]
events_file_path = "scripts/sportsevents.txt"
embeddings_file_path = "models/events.npy"
def run_pipeline():
    #need to use appending to file since using for loop
    #easier to just remove the file everytime and make a new one
    os.remove('events_file_path')
    lookup_events(event_ids, events_file_path)
    
    encode_events()
    
    update_embed()

    genTweet()

run_pipeline()



