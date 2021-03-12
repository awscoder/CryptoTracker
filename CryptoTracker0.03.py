import sqlite3 as lite
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

create_holdings_table = "CREATE TABLE Holdings(Coin_held TEXT, Amt_held REAL, Net_cost REAL, Cost_per_coin REAL);"
insert_user_inputted_holdings = "INSERT INTO Holdings(Coin_held, Amt_held) VALUES(?, ?);"
create_transactions_table = "CREATE TABLE Transactions(Date_pur NUMERIC, Coin_pur TEXT, Amt_coin_pur REAL, Price_per_coin REAL, Coin_sold TEXT, Amt_coin_sold REAL, Exchange_of_trx TEXT, If_taxable TEXT, FMV_coin_sold REAL, If_sold TEXT, Cur_held_loc TEXT, Amt_sold REAL, Date_sold NUMERIC, ID INTEGER PRIMARY KEY);"
insert_fills = "INSERT INTO Transactions (Date_pur, Coin_pur, Amt_coin_pur, Price_per_coin, Coin_sold, Amt_coin_sold, Exchange_of_trx, If_taxable, FMV_coin_sold, If_sold) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, 'NO');"
update_holdings_from_fills = "UPDATE Holdings SET Amt_held = ?, Net_cost = ? WHERE Coin_held = ?;"
get_amt_by_coin = "SELECT * FROM Holdings WHERE Coin_held = ?;"
add_0_holding = "INSERT INTO Holdings VALUES(?, ?, ?, ?);"
calc_cpc = "UPDATE Holdings SET Cost_per_coin = Net_cost / Amt_held;"
create_taxes_table = "CREATE TABLE Taxes(Coin_sold TEXT, Amt_coin_sold REAL, Date_pur NUMERIC, Date_sold NUMERIC, Proceeds REAL, Cost REAL, Gains REAL, Exchange_of_trx TEXT, ID INTEGER PRIMARY KEY);"
sales_to_gains_fifo = "INSERT INTO Taxes (Coin_sold, Amt_coin_sold, Date_pur, Date_sold, Proceeds, Cost, Gains, Exchange_of_trx) VALUES(?, ?, ?, ?, ?, ? , ?, ?);"
get_taxable_txns = "SELECT * FROM Transactions WHERE If_taxable = 'YES';"
get_unsold_buys = "SELECT * FROM Transactions WHERE If_sold = 'NO';"
get_taxes = "SELECT * FROM Taxes;"
update_taxes = "UPDATE Taxes SET Date_pur = ?, Cost = ?, Gains = ? WHERE ID = ?;"
update_txns_sold = "UPDATE Transactions SET If_sold = ?, Amt_sold = ?, Date_sold = ? WHERE ID = ?;"

# sales_to_gains_fifo = "SELECT Coin_sold, Amt_coin_sold, Date_pur, Date_sold, FMV_coin_sold, Exchange_of_trx, If_taxable,
#        CASE WHEN If_taxable = 'YES' THEN #'over 250'
#             ELSE END AS If_taxable
#   FROM Transactions;"

def create_db():
    name_database = input("What would you like to name your database? (use .db extension): ")
    con = lite.connect(name_database) #DB that stores user data
    cur = con.cursor()
  
    with con:     
        cur.execute(create_transactions_table)
        cur.execute(create_holdings_table)
        cur.execute(create_taxes_table)

    con.commit()
    return name_database
def user_input_holdings():
    user_holdings = [('EX', 'EX')] #Junk values to get the while loop to work
    while user_holdings [-1][0] != 'DONE': #Loops until the user leaves the coin name blank
        coin = (input("Type the coin to add to your holdings (e.g. BTC) (Enter when done adding): ") or 'DONE') #sets value to 'Done' on a blank
        if coin.isalpha():
            coin = coin.upper()
        elif coin.isdigit():
            print("Please type the NAME of the coin (letters only)")
            coin = 'BAD_INPUT'
        amt = (input("Type the number of these coins to add to your holdings (e.g 0.05) (Enter when done adding): ") or 'DONE')
        try:
            if amt == 'DONE' and coin == 'DONE':
                print("Thank you for adding your coins!")
            else:
                amt = float(amt)
        except:
            print("Please type the NUMBER of coins (Digits and decimals only)")
            amt = 'BAD_INPUT'

        user_defined_holdings = (coin, amt)
        user_holdings.append(user_defined_holdings)
    user_holdings = user_holdings[1:-1] #Remove the junk first and last tuple
    print(user_holdings) #Before removing bad inputs
    i = 0
    while i < len(user_holdings):
        if (user_holdings[i][0] == 'BAD_INPUT') or (user_holdings[i][1] == 'BAD_INPUT'):
            user_holdings.pop(i) #Removes any tuple with 'BAD_INPUT'
        else: #Only increases i after checking for 'BAD_INPUT' because the index decreases after a pop() so two "BAD_INPUTS" in a row would resutl in the second being left
            i += 1
    print(user_holdings, "(Bad inputs removed)") #After removing bad inputs
    return user_holdings

def user_import_CBP():
    user_fills_csv = input("Enter the filename of the CBP fills file (ENTER for default fills.csv): ") or 'fills.csv'
    with open(user_fills_csv, 'r') as cbpinfile: #CBP csv file (fills.csv)
        transactions = []
        for row in cbpinfile:
            cells = row.split(',')
            cells = list(cells)
            if cells[10][-1:] == '\n': #CBP sometimes adds newline characters to names in column 10, removes those
                cells[10] = cells[10][:-1]
            if cells[9][0] == '-': #CBP lists transactions where USD is used to purchase as a negative amount, removes '-' for later math consistency
                cells[9] = cells[9][1:]
            cells[4] = cells[4][8:10] + cells[4][4:8] + cells[4][0:4]

            cells = (cells[3], cells[4], cells[6], cells [5], cells[7], cells[10], cells[9]) #Makes a tuple where each element matches the Transactions table headings
            transactions.append(cells) #After for loop, the list transactions now has all the data from the csv formated for use
    cbpinfile.close()
    transactions = transactions[1:] #Removes the csv file's headers from the list
    return (transactions, 'CBP')

def user_import_BinanceUS():
    print('Not Binance Support Yet')

def user_generic_import_fills():
    exch = input("What would you like to be listed as the exchange name for these transactions: ")
    user_fills_csv = input("Enter the filename of the fills file (include .csv in name): ")
    with open(user_fills_csv, 'r') as infile:
        transactions = []
        for row in infile:
            cells = row.split(',')
            cells = list(cells)
            transactions.append(cells)
    infile.close()
    transactions = transactions[1:] #Removes the csv file's headers from the list
    return(transactions, exch)
    
def add_holdings_by_hand(db):
    con = lite.connect(db) #DB that stores user data
    cur = con.cursor()
    user_new_holdings = user_input_holdings()

    with con:
        for i in range(len(user_new_holdings)):
            cur.execute(insert_user_inputted_holdings, (user_new_holdings[i][0], user_new_holdings[i][1]))
    con.commit()

def update_transactions_and_holdings_with_formated_fills(name_database, formated_fills_list, exchange, currencies, dict_of_coins_CG):
    '''tx equivalents: 0 - Buy/Sell, 1 - Date_pur, 2 Coin_pur, 3 Amt_coin_pur, 4 Price_per_coin, 5 Coin_sold, 6 Amt_coin_sold'''
    con = lite.connect(name_database)
    cur = con.cursor()
    str_currencies = ((str(currencies).lower())[1:-1])
    with con:     
        for tx in formated_fills_list:
            con.commit()
            is_taxable = ""
            coin_selling_price = "NULL"
            date_of_sale = tx[1]
            name_coin_pur = tx[2]
            amt_coin_pur = float(tx[3])
            ppc = float(tx[4])
            name_coin_sold = tx[5]
            amt_coin_sold = float(tx[6])
            cg_name_coin_pur = name_coin_pur.lower()
            cg_name_coin_sold = name_coin_sold.lower()
            
#             for i in range(len(dict_of_coins_CG)):
#                 if cg_name_coin_pur not in str_currencies:
#                     if dict_of_coins_CG[i]['symbol'] == cg_name_coin_pur:
#                         cg_name_coin_pur = dict_of_coins_CG[i]['id']
#                         break
#                 if cg_name_coin_sold not in str_currencies:
#                     if dict_of_coins_CG[i]['symbol'] == cg_name_coin_sold:
#                         cg_name_coin_sold = dict_of_coins_CG[i]['id']
#                         break
            if cg_name_coin_pur not in str_currencies and cg_name_coin_sold not in str_currencies:
                try: #If one of the coins can't be found on CG, it will raise the except statement which will ask for user input
                    cg_name_coin_pur = (next(item for item in dict_of_coins_CG if item["symbol"] == cg_name_coin_pur))['id']
                    cg_name_coin_sold = (next(item for item in dict_of_coins_CG if item["symbol"] == cg_name_coin_sold))['id']
                except StopIteration:
                    is_taxable = "YES"
                    coin_selling_price = "UNKNOWN COIN"
                    if tx[0] == "BUY":
                        coin_selling_price = float(input("Enter the price of " + name_coin_sold + " for " + date_of_sale + ": "))
                        amt_held_buying = get_cur_holdings(name_database, name_coin_pur) #Current holdings for the given coin
                        amt_held_selling = get_cur_holdings(name_database, name_coin_sold)
                        cur.execute(update_holdings_from_fills, ((amt_held_buying[0] + amt_coin_pur), (amt_held_buying[1]+amt_coin_sold), name_coin_pur)) #updates holdings
                        cur.execute(update_holdings_from_fills, ((amt_held_selling[0] - amt_coin_sold), (amt_held_selling[1]-amt_coin_pur), name_coin_sold))
                        cur.execute(insert_fills, (date_of_sale, name_coin_pur, amt_coin_pur, ppc, name_coin_sold, amt_coin_sold, exchange, is_taxable, (coin_selling_price*amt_coin_sold))) #adds the tranasction to the Transaction table
                    elif tx[0] == "SELL":
                        coin_selling_price = float(input("Enter the price of " + name_coin_pur + " for " + date_of_sale + ": "))
                        amt_held_buying = get_cur_holdings(name_database, name_coin_sold)
                        amt_held_selling = get_cur_holdings(name_database, name_coin_pur)
                        cur.execute(update_holdings_from_fills, ((amt_held_buying[0] + amt_coin_sold), (amt_held_buying[1] + (amt_coin_pur * coin_selling_price)), name_coin_sold))
                        cur.execute(update_holdings_from_fills, ((amt_held_selling[0] - amt_coin_pur), (amt_held_selling[1]-(amt_coin_pur * coin_selling_price)), name_coin_pur))
                        cur.execute(insert_fills, (date_of_sale, name_coin_sold, amt_coin_sold, (1/ppc), name_coin_pur, amt_coin_pur, exchange, is_taxable, (coin_selling_price*amt_coin_pur)))
                    continue

            if tx[0] == "BUY":
                if name_coin_sold not in currencies: #If a you sell one crypto for another, it is taxable
                    is_taxable = "YES"
                    try:
                        hist_dict = cg.get_coin_history_by_id(id=cg_name_coin_sold, date=date_of_sale)
                        coin_selling_price = hist_dict['market_data']['current_price'][currencies[0].lower()]
                    except:
                        coin_selling_price = float(input("Enter the price of " + name_coin_sold + " for " + date_of_sale + ": "))
                else:
                    is_taxable = "NO"
                    coin_selling_price = 1.0
                amt_held_buying = get_cur_holdings(name_database, name_coin_pur) #Current holdings for the given coin
                amt_held_selling = get_cur_holdings(name_database, name_coin_sold)
                cur.execute(update_holdings_from_fills, ((amt_held_buying[0] + amt_coin_pur), (amt_held_buying[1]+amt_coin_sold), name_coin_pur)) #updates holdings
                cur.execute(update_holdings_from_fills, ((amt_held_selling[0] - amt_coin_sold), (amt_held_selling[1]-amt_coin_pur), name_coin_sold))
                cur.execute(insert_fills, (date_of_sale, name_coin_pur, amt_coin_pur, ppc, name_coin_sold, amt_coin_sold, exchange, is_taxable, (coin_selling_price*amt_coin_sold))) #adds the tranasction to the Transaction table
            elif tx[0] == "SELL":
                '''Note names are the inverse of what you might expect for pur and sold bc these are sell orders'''
                is_taxable = "YES"
                if name_coin_sold in currencies: #If a you sell your crypto for fiat
                    coin_selling_price = 1.0
                else: #If you sell crypto for crypto
                    try:
                        hist_dict = cg.get_coin_history_by_id(id=cg_name_coin_pur, date=date_of_sale)
                        coin_selling_price = hist_dict['market_data']['current_price'][currencies[0].lower()]
                    except:
                        coin_selling_price = float(input("Enter the price of " + name_coin_pur + " for " + date_of_sale + ": "))
                amt_held_buying = get_cur_holdings(name_database, name_coin_sold)
                amt_held_selling = get_cur_holdings(name_database, name_coin_pur)
                cur.execute(update_holdings_from_fills, ((amt_held_buying[0] + amt_coin_sold), (amt_held_buying[1] + (amt_coin_pur * coin_selling_price)), name_coin_sold))
                cur.execute(update_holdings_from_fills, ((amt_held_selling[0] - amt_coin_pur), (amt_held_selling[1]-(amt_coin_pur * coin_selling_price)), name_coin_pur))
                if coin_selling_price == 1.0:
                    cur.execute(insert_fills, (date_of_sale, name_coin_sold, amt_coin_sold, (1/ppc),
                                           name_coin_pur, amt_coin_pur, exchange, is_taxable, (amt_coin_sold)))
                else:
                    cur.execute(insert_fills, (date_of_sale, name_coin_sold, amt_coin_sold, (1/ppc),
                                           name_coin_pur, amt_coin_pur, exchange, is_taxable, (coin_selling_price*amt_coin_pur)))
        cur.execute(calc_cpc)
        con.commit()
    

def get_cur_holdings(name_database, coin):
    con = lite.connect(name_database)
    cur = con.cursor()
    with con:
        held = cur.execute(get_amt_by_coin, (coin,)).fetchall() 
    try:
        held = held.pop() #Checks if the given coin is in the Holdings table, if it is, except is skipped.
    except:
        cur.execute(add_0_holding, (coin, 0.0, 0.0, 0.0)) #Adds the coin to the Holdings table with 0.0 for the amt_held
        con.commit()
        held = ('N/A', 0.0, 0.0, 0.0)
    amt_held = (float(held[1]), float(held[2]))  #Converts list into a float of the current amount held
    return amt_held

def generate_tax_data(name_database):
    con = lite.connect(name_database)
    cur = con.cursor()
    date_pur = 'Undetermined'
    cost = 0.0
    with con:
        txns = cur.execute(get_taxable_txns).fetchall()
        for tup in txns:
            gains = float(float(tup[8]) - cost)
            cur.execute(sales_to_gains_fifo, (tup[4], tup[5], date_pur, tup[0], tup[8], cost, gains, tup[6]))
            con.commit()
                
#         buys = cur.execute(get_unsold_buys).fetchall()
#         taxes = cur.execute(get_taxes).fetchall()
#         for tup in taxes:
#             try:
#                 idx = (next(item for item in buys if item[1] == tup[0]))
#                 values = [idx[0], idx[2], idx[8]] #[date_pur, amt_pur, FMV_of_pur]
#                 gains = float(tup[4]) - values[2]
#                 cur.execute(update_taxes, (values[0], values[2], gains, tup[8]))
#             except:
#                 values = [idx[0], idx[2], idx[8]] #[date_pur, amt_pur, FMV_of_pur]
#                 gains = float(tup[4]) - values[2]
#                 cur.execute(update_taxes, (values[0], values[2], gains, tup[8]))
#             try:
#                 prev_sold = float(idx[11])
#             except:
#                 prev_sold = 0.0
#             if (float(idx[2]) - prev_sold - float(tup[1])) <= 0.0:
#                 if_sold = "YES"
#             else:
#                 if_sold = "PARTIAL"
#             cur.execute(update_txns_sold, (if_sold, tup[1], tup[3], idx[13]))
#             con.commit()

# def update_tax_pur_cost():
    

def main(): #Testcase with CBP fills.csv
    coin_dict = cg.get_coins_list()
    user_currencies = ['USD', 'USDC', 'GUSD'] #(Make first currency your local fiat e.g. 'USD') Any currencies used which would not be taxable to sell (i.e. fiat and stablecoins)
    user_database_name = create_db() #Generates the initial database with Holdings and Transactions tables
    (formated_list_CBP, exchange) = user_import_CBP() #Lets the user import the CBP fills.csv file
    update_transactions_and_holdings_with_formated_fills(user_database_name, formated_list_CBP, exchange, user_currencies, coin_dict)  #Takes formatted CBP data and edits the database
    generate_tax_data(user_database_name)
#     coin_hist_fmv = cg.get_coin_history_by_id(id='bitcoin', vs_currencies=user_currencies[0].lower(), date='26-11-2020')
#     print(coin_hist_fmv)
main()
