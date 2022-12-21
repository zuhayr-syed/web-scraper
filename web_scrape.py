from bs4 import BeautifulSoup
import requests
import re
from decimal import Decimal
import csv

"""
Define const and functions
"""
# const
printLine = '-------------------------------------------------------------------------------------------------------'
rowTitle = ['Name', 'Price', 'Shipping Price', 'Total Price', 'Link']
# makes get request to page 
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
def extract(page):
    link = f'https://www.newegg.ca/p/pl?d={product}&N=4131&page={page}'
    page = requests.get(link, headers).text
    return BeautifulSoup(page, 'html.parser')
# remove extra zeros on price
def remove_exponent(d):
    return d.quantize(Decimal(1)) if d == d.to_integral() else d.normalize()


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
            
            price = main_parent.find(class_='price-current')
            dollar = price.strong.string
            cent = price.sup.string
            sum = dollar + cent
            
            shipping = main_parent.find(class_='price-ship').string
            
            sum = sum.replace(',', '')
            sum = remove_exponent(Decimal(sum))

            if shipping.__contains__('$'):
                shipping = shipping[1:-9]
                shipping = remove_exponent(Decimal(shipping))
        
                total = sum + shipping
            else:
                total = sum
            
            centFormat = str(total)[-2:]
            if centFormat.__contains__('.'):
                total = str(total) + '0'
            else:
                centFormat = str(total)[-3:]
                if not centFormat.__contains__('.'):
                    total = str(total) + '.00'
            
            itemsList[item] = {'price': sum, 'shipping': shipping, 'total': total, 'link': link}

    # sort dictionary based on price
    sorted_items = sorted(itemsList.items(), key=lambda x: x[1]['total'])
    
    for item in sorted_items:
        print(item[0])
        print(f"${item[1]['price']}")
        if str(item[1]['shipping'])[0].isdigit():
            print(f"${item[1]['shipping']}.00")
        else:
            print(item[1]['shipping'])
        print(f"${item[1]['total']}")
        print(item[1]['link'])
        print(printLine)
    
    # create csv file
    with open(product + '.csv', 'w') as file:
        writer = csv.writer(file)
