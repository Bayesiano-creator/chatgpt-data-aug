import os

os.environ["REPLICATE_API_TOKEN"] = "YOUR_API_TOKEN"

# Parameters

_SUBTASK_ = 1

if _SUBTASK_ == 1:    
    _PROMPT_ = 'Suppose there is a twitter user who is a cryptocurrency influencer and their class of influence is {label} influencer. They wrote the next tweets:\n\n{listed_tweets}\n\nBased on these tweets, invent a new user who also is a {label} cryptocurrency influencer and write a new tweet of that user here:'

elif _SUBTASK_ == 2:
    _PROMPT_ = 'Suppose there is a twitter user who is a cryptocurrency influencer with interest in {label}. They wrote the next tweets:\n\n{listed_tweets}\n\nBased on these tweets, invent a new user who also is a cryptocurrency influencer with interest in {label} and write a new tweet of that user here:'

elif _SUBTASK_ == 3:
    _PROMPT_ = 'Suppose there is a twitter user who is a cryptocurrency influencer with {label} intent. They wrote the next tweets:\n\n{listed_tweets}\n\nBased on these tweets, invent a new user who also is a cryptocurrency influencer with {label} intent and write a new tweet of that user here:'


## Get data

def get_DATA(dir, subtask, file):
    
    json_data = jsonl.open(dir+'subtask'+str(subtask)+'/'+file+'_text.json') 
    tweets = {}
    for line in json_data:
        author    = line['twitter user id']
        texts     = [inst['text'] for inst in line['texts']]
        tweet_ids = [inst['tweet id'] for inst in line['tweet ids']]

        tweets[author] = list( zip(tweet_ids, texts) )
        
    json_data = jsonl.open(dir+'subtask'+str(subtask)+'/'+file+'_truth.json')
    labels = {}
    for line in json_data:
        labels[ line['twitter user id'] ] = line['class']

    return tweets, labels

tweets, labels = get_DATA(dir = 'data/2023/', subtask = _SUBTASK_, file = 'train')
authors = list( tweets.keys() )

## Author generator function with ChatGPT API

import openai

def generate_author(author, tweets, label, prompt_format):
    listed_tweets = ''
    for i, tweet in enumerate(tweets):
        listed_tweets += tweet[1] + '\n'   
    
    prompt = prompt_format.format(listed_tweets = listed_tweets, label = label)
    
    openai.api_key = s.getenv("OPENAI_API_KEY")
    response = openai.Completoion.create(
        engine="",
        prompt=prompt,
        max_tokens=128,
        n=len(tweets),
        stop=None,
        temperature=1.0,
    )
    generated  = response.choices
    new_tweets = [ (tweet[0], choice.text.strip()) for tweet, choice in zip(tweets, generated)]
        
    return new_tweets

## Generate and save new authors

new_dir = 'data/2023gpt/'

from tqdm import tqdm
import json
import time

pbar = tqdm(authors)

texts_file = open(new_dir + 'subtask' + str(_SUBTASK_) + '/train_text.json', 'w')
truth_file = open(new_dir + 'subtask' + str(_SUBTASK_) + '/train_truth.json', 'w')

for author in pbar:
    new_author = author + '_prompt1_1'
    new_tweets = generate_author(author, tweets[author], labels[author], _PROMPT_)
    
    inst = {}
    inst['twitter user id'] = new_author
    inst['texts']           = [{'text': tweet} for id,tweet in new_tweets]
    inst['tweet ids']       = [{'tweet id': id} for id,tweet in new_tweets]

    json.dump(inst, texts_file)
    texts_file.write('\n')
    
    truth = {}
    truth['twitter user id'] = new_author
    truth['class']           = labels[author]
    
    json.dump(truth, truth_file)
    truth_file.write('\n')
    
    time.sleep(1)
    
texts_file.close()
truth_file.close()
