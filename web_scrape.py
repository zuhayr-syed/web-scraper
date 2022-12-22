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
rowTitle = ['Name', 'Price', 'Shipping Price', 'Total Price', 'Rating', 'Link']
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
            
            ratingParent = main_parent.find(class_='item-rating')
            rating = ""
            if ratingParent != None:
                rating = ratingParent.i['aria-label'][6:-9] + '/5'
            
            itemsList[item] = {'price': sum, 'shipping': shipping, 'total': total, 'rating': rating, 'link': link}

    # sort dictionary based on price
    sorted_items = sorted(itemsList.items(), key=lambda x: x[1]['total'])
    
    csvList = []
    
    for item in sorted_items:
        csvRow = []
        
        name = item[0]
        print(name)
        csvRow.append(name)
        
        price = f"${item[1]['price']}"
        print(price)
        csvRow.append(price)
        
        if str(item[1]['shipping'])[0].isdigit():
            shipping = f"${item[1]['shipping']}.00"
            print(shipping)
            csvRow.append(shipping)
        else:
            shipping = item[1]['shipping']
            print(shipping)
            csvRow.append(shipping)
        
        total = f"${item[1]['total']}"
        print(total)
        csvRow.append(total)
        
        rating = item[1]['rating']
        print(rating)
        csvRow.append(rating)
        
        link = item[1]['link']
        print(link)
        csvRow.append(link)
        
        print(printLine)
        csvList.append(csvRow)
    
    # create csv file
    with open(product + '.csv', 'w') as file:
        writer = csv.writer(file)
        
        writer.writerow(rowTitle)
        for row in csvList:
            writer.writerow(row)
