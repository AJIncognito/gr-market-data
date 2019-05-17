import requests
import bs4
import lxml
import datetime
# from selenium import webdriver
# import time
# print("Imports complete, starting execution...")

# URLs for the bond data
GGB10_url = 'https://www.investing.com/rates-bonds/greece-10-year-bond-yield-historical-data'
GGB5_url = 'https://www.investing.com/rates-bonds/greece-5-year-bond-yield-historical-data'
GGB20_url = 'https://www.investing.com/rates-bonds/greece-3-year-bond-yield-historical-data'
#ASE_url = 'https://www.bloomberg.com/quote/ASE:IND'
Helex_url = 'http://www.helex.gr/indices'

# needed to allow scraping from investing.com
header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}

#function to pull stock data
def getStockData():
  r = requests.get(Helex_url, headers=header)
  soup_obj = bs4.BeautifulSoup(r.text, 'lxml')
  soup_obj.prettify()
  #print('\nProcessing ATHEX data...')
  stock_values = soup_obj.find_all(class_='index-amt')
  #print(stock_values)
  price = float(stock_values[0].text)
  previous_close_value = float(stock_values[1].text)
  return price, previous_close_value

# function to pull bond data
def getBondData(GGB_version):
  r = requests.get(GGB_version, headers=header)
  soup_obj = bs4.BeautifulSoup(r.text, 'lxml')
  soup_obj.prettify()
  current_bond_value = soup_obj.find(class_='arial_26')

  current_price = float(current_bond_value.text)

  historical_price_table = soup_obj.find(id = 'curr_table')

  big_list_of_cells = []
  # table format is Date, Price,
  for row in historical_price_table.findAll('tr'):
    list_of_cells = []
    for cell in row.findAll('td'):
      if '%' in cell.text:
        list_of_cells.append(cell.text)
      elif '.' in cell.text:
        list_of_cells.append(float(cell.text))
      else:
        list_of_cells.append(cell.text)
    big_list_of_cells.append(list_of_cells)

  old_prices = big_list_of_cells[6]

  return current_price, old_prices

# function to create arbitrary-length strings
def str_append(s, n):
    output = ''
    i = 0
    while i < n:
        output += s
        i = i + 1
    return output


## Main function begins here
# pull and unpack all the bond price datasets
print("Running script...")
ten_year = getBondData(GGB10_url)
current_10 = ten_year[0]
(prior_date_10, old_price_10, old_open_10, old_high_10, old_low_10, change_10) = ten_year[1]

five_year = getBondData(GGB5_url)
current_5 = five_year[0]
(prior_date_5, old_price_5, old_open_5, old_high_5, old_low_5, change_5) = five_year[1]

twenty_year = getBondData(GGB20_url)
current_20 = twenty_year[0]
(prior_date_20, old_price_20, old_open_20, old_high_20, old_low_20, change_20) = twenty_year[1]

# figure out whether things are up, down, or mixed
if (current_5 > old_price_5) and (current_10 > old_price_10) and (current_20 > old_price_20):
  bond_change = 'down'
  bond_change_short = u'\u2193'
elif (current_5 < old_price_5) and (current_10 < old_price_10) and (current_20 < old_price_20):
  bond_change = 'up'
  bond_change_short = u'\u2193'
else:
  bond_change = 'mixed'
  bond_change_short = 'mixed'

# also get ATHEX data and figure out if things are going up or down
(stock_price, stock_change) = getStockData()
if stock_change >= 0:
  stock_movement = 'up'
  stock_movement_short = u'\u2191'
else:
  stock_movement = 'down'
  stock_movement_short = u'\u2193'

today = datetime.datetime.now()
# Output the results
print(f'\nGreece Market Update for {today.strftime("%A, %B %d, %Y")}:  Bourse {stock_movement_short}, Bonds {bond_change_short}:')

stock_percent = "{:.2%}".format(stock_change / (stock_price - stock_change))
print(f'\n  As of {today.strftime("%-I:%M %p")}, the ATHEX composite index is at {stock_price}, {stock_movement} {stock_change} points ({stock_percent}) from open.')

bond_string = 'Bond yields are ' + bond_change + ':'
print(f'\n  {bond_string}')

character_buffer = str_append('-', len(bond_string))
print(f'  {character_buffer}')
print(f'   5-Year: {current_5:.3f}  Previous: {old_price_5:.3f}')
print(f'  10-Year: {current_10:.3f}  Previous: {old_price_10:.3f}')
print(f'  20-Year: {current_20:.3f}  Previous: {old_price_20:.3f}')



#f = open('output.txt', 'w')
#f.write(f'{bond_string}\n')
#f.write(f'  5-Year: {current_5:.3f}\tPrevious: {old_price_5:.3f}\n')
#f.close()
