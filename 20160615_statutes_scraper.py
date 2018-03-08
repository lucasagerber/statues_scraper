

from bs4 import BeautifulSoup
import urllib.request
import time
import re
from collections import defaultdict
import os
import pandas as pd


# Link for state statutes search
link = 'https://www.childwelfare.gov/topics/systemwide/laws-policies/state/'

# Open link, read, and convert to beautiful soup 
with urllib.request.urlopen(link) as url:
    url_html = url.read()

url_soup = BeautifulSoup(url_html, 'html.parser')

# Test that it worked
print(url_soup.prettify())



# Gather topics and states from website
topics = [result['value'] for result in url_soup.find_all(id='topicIDs')]
states = [result['value'] for result in url_soup.find_all('option')]

# Test that it worked
print(topics)
print(states)



# Link to search the database
link_search = 'https://www.childwelfare.gov/topics/systemwide/laws-policies/state/?CWIGFunctionsaction=statestatutes:main.getResults'

# Root folder to write into
root = 'C:/Users/Lucas/Documents/NDACAN SRI/Analysis/statutes/'

# Function to pull data from website -- waits when server gives an error from too many downloads
def pull_data(link, data_post, state, topic):
    try:
        with urllib.request.urlopen(link, data=data_post) as search_url:
            print(state,topic)
            search_html = search_url.read()
            search_soup = BeautifulSoup(search_html, 'html.parser')
            time.sleep(1)
            return search_soup.find(id='content')
    except:
        print('Error: waiting 2 minutes')
        time.sleep(120)
        result =  pull_data(link, data_post, state, topic)
        return result

# Loop through each state and topic, search website and save output to text files in root directory
state_statutes = {}
for state in states:
    for topic in topics:
        data_post = 'states=' + state + '&topicIDs=' + topic
        data_post = data_post.encode()

        search_soup = pull_data(link_search, data_post, state, topic)  

        # Delete headers
        search_soup.h2.decompose()
        search_soup.h2.decompose()
        search_soup.h3.decompose()
        
        output = search_soup.get_text(' ', strip=True)
        
        # Delete introductory and closing texts
        for string in ['\( Back to Top \)', 'To better understand .+of this publication\.']:
            output = re.sub(string, '', output)

        file_name = root + state + topic + '.txt'
        with open(file_name,'w') as f_out:
            f_out.write(output.strip())



# Combine into dictionary for dataframe
statutes_dict = defaultdict(dict)
for file in os.listdir(root):
    file_name = root + file
    with open(file_name) as f_in:
        key = file.split('.')[0]
        state = key[:2]
        statute_number = int(key[2:])
        statutes_dict[state][statute_number] = f_in.read()

# Convert into dataframe
statutes_df = pd.DataFrame(statutes_dict).transpose()

# Save to csv
statutes_df.to_csv('C:/Users/Lucas/Documents/NDACAN SRI/Analysis/statutes_df.csv')



