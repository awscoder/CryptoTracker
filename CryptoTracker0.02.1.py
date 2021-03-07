import sqlite3 as lite

create_holdings_table = "CREATE TABLE Holdings(Coin_held TEXT, Amt_held REAL);"
insert_user_inputted_holdings = "INSERT INTO Holdings VALUES(?, ?);"
create_transactions_table = "CREATE TABLE Transactions(Date_pur NUMERIC, Coin_pur TEXT, Amt_coin_pur REAL, Price_per_coin REAL, Coin_sold TEXT, Amt_coin_sold REAL, Exchange_of_trx TEXT, If_sold TEXT, Cur_held_loc TEXT, Amt_sold REAL, Date_sold NUMERIC);"
insert_fills = "INSERT INTO Transactions (Date_pur, Coin_pur, Amt_coin_pur, Price_per_coin, Coin_sold, Amt_coin_sold, Exchange_of_trx) VALUES(?, ?, ?, ?, ?, ?, ?);"
update_holdings_from_fills = "UPDATE Holdings SET Amt_held = ? WHERE Coin_held = ?"
get_amt_by_coin = "SELECT Amt_held FROM Holdings WHERE Coin_held = ?"
add_0_holding = "INSERT INTO Holdings VALUES(?, ?);"

def create_db():
    name_database = input("What would you like to name your database? (use .db extension): ")
    con = lite.connect(name_database) #DB that stores user data
    cur = con.cursor()
  
    with con:     
        cur.execute(create_transactions_table)
        cur.execute(create_holdings_table)

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

            cells = (cells[3], cells[4], cells[6], cells [5], cells[7], cells[10], cells[9]) #Makes a tuple where each element matches the Transactions table headings
            transactions.append(cells) #After for loop, the list transactions now has all the data from the csv formated for use
    cbpinfile.close()
    transactions = transactions[1:] #Removes the csv file's headers from the list
    print(transactions)
    return (transactions, 'CBP')

def user_import_BinanceUS():
    print('yoffufu')

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

def update_transactions_and_holdings_with_formated_fills(name_database, formated_fills_list, exchange):
    con = lite.connect(name_database)
    cur = con.cursor()
    with con:     
        for tx in formated_fills_list:
            con.commit()
            if tx[0] == "BUY":
                amt_held_buying = (get_cur_holdings(name_database, tx[2])) #Current holdings for the given coin
                amt_held_selling = (get_cur_holdings(name_database, tx[5]))
                cur.execute(update_holdings_from_fills, ((amt_held_buying + float(tx[3])), tx[2])) #updates holdings
                cur.execute(update_holdings_from_fills, ((amt_held_selling - float(tx[6])), tx[5]))
                cur.execute(insert_fills, (tx[1], tx[2], float(tx[3]), float(tx[4]), tx[5], float(tx[6]), exchange)) #adds the tranasction to the Transaction table
            elif tx[0] == "SELL":
                amt_held_buying = get_cur_holdings(name_database, tx[5])
                amt_held_selling = (get_cur_holdings(name_database, tx[2]))
                cur.execute(update_holdings_from_fills, ((amt_held_buying + float(tx[6])), tx[5]))
                cur.execute(update_holdings_from_fills, ((amt_held_selling - float(tx[3])), tx[2]))
                cur.execute(insert_fills, (tx[1], tx[5], float(tx[6]), 1/(float(tx[4])), tx[2], float(tx[3]), exchange))
    
def get_cur_holdings(name_database, coin):
    con = lite.connect(name_database)
    cur = con.cursor()
    with con:
        held = cur.execute(get_amt_by_coin, (coin,)).fetchall() 
    try:
        held = held.pop() #Checks if the given coin is in the Holdings table, if it is, except is skipped.
    except:
        cur.execute(add_0_holding, (coin, 0.0)) #Adds the coin to the Holdings table with 0.0 for the amt_held
        con.commit()
        held = [(0.0)]
    amt_held = float(held[0]) #Converts list into a float of the current amount held
    return amt_held

def main(): #Testcase with CBP fills.csv
    user_database_name = create_db() #Generates the initial database with Holdings and Transactions tables
    # (formated_list_CBP, exchange) = user_import_CBP() #Lets the user import the CBP fills.csv file
    # update_transactions_and_holdings_with_formated_fills(user_database_name, formated_list_CBP, exchange)  #Takes formatted CBP data and edits the database
    (formatted_list, exchange) = user_generic_import_fills()
    update_transactions_and_holdings_with_formated_fills(user_database_name, formatted_list, exchange)
    
main()