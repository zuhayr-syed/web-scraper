from bs4 import BeautifulSoup
import requests
import re

printLine = '-------------------------------------------------------------------------------------------------------'

# makes get request to page 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
def extract(page):
    link = f'https://www.newegg.ca/p/pl?d={product}&N=4131&page={page}'
    page = requests.get(link, headers).text
    return BeautifulSoup(page, 'html.parser')

"""
Scrapes data from Newegg for a searched product 
"""

product = input("What product do you want to search for? ")

# grab base page
doc = extract(1)

# not found error check
error = doc.find(class_='result-message-error')
if error:
    print('\n' + printLine + '\n' + 'ERROR WITH SEARCH: ' + error.text + '\n' + printLine + '\n')
else:
    print('\n' + printLine + '\n' + 'LOADING RESULTS...' + '\n' + printLine + '\n')
    
    # find number of pages
    page_text = doc.find(class_='list-tool-pagination-text').strong.text
    pages = int(page_text[2])
    for page in range(1, pages + 1):
        doc = extract(page)
        div = doc.find(class_='item-cells-wrap border-cells items-grid-view four-cells expulsion-one-cell')
        
        # find items that contain the search in name using regular expression
        items = div.find_all(text=re.compile(product))

        itemsList = {}

        for item in items:
            parent = item.parent
            if parent.name != 'a':
                # for items that are not a listing and dont have a link
                continue
            link = parent['href']
            
            main_parent = item.find_parent(class_='item-container')
            price = main_parent.find(class_='price-current').strong.string
            
            itemsList[item] = {"price": price, "link": link}
    print(itemsList)

    
