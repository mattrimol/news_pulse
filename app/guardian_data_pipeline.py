"""This is the library to connect to the API and get JSON documents from URL requests"""

import requests
import pandas as pd

api_key = '9c568510-de68-4f92-865a-04ce14b7e78a'
url = f'https://content.guardianapis.com/search?\
                from-date=<start>&\
                to-date=<end>&\
                order-by=newest&\
                page=<page>&\
                page-size=200&\
                api-key={api_key}'


def get_results_list(url):
    """
    Takes in a url:
        Start and end date must be specified in url
        The page number should be '<page>' and the function will page through all results
    total results must be < 36,000
    Returns a list of dictionaries, each dictionary represents a story/article from results
    """
    
    url = url.replace(' ', '')
    #print(url)
    
    #Getting the first page
    response = requests.get(url.replace('<page>', '1'))
    json_dict = response.json()
    #print(json_dict)
    
    #We will use this to know how much to page through
    num_pages = json_dict['response']['pages']
    
    #Getting the list of results from the json dictionary for the first page
    results_list = json_dict['response']['results']
    
    request_count = 1
    
    #Getting the list of results from page 2 through the last page and adding it to the list we created with page 1
    for i in range(2, num_pages + 1):
        page = i
        #print(url)
        page_response = requests.get(url.replace('<page>', str(i)))
        request_count += 1
        page_json_dict = page_response.json()
        try:
            page_results_list = page_json_dict['response']['results']
        except KeyError:
            print(f'Error on page{i}')
            print(page_json_dict)
        #Master list that is growing with each page added    
        results_list += page_results_list
    print(f'Requests used: {request_count}')
    return results_list

def results_list_to_df(results_list):
    #Give indexes as keys to the articles so it can be made into df
    results_list = {i: story for i, story in enumerate(results_list)}
    df = pd.DataFrame.from_dict(results_list, orient='index')
    
    return df

def clean_df(df):
    #Create column with published datetime as a pandas datetime64
    df['pub_datetime'] = pd.to_datetime(df['webPublicationDate'])
    
    #Drop unneeded columns
    df.drop(columns = ['webPublicationDate',
                               'apiUrl',
                               'isHosted',
                               'pillarId'],
                              axis=1, inplace=True)
    return df