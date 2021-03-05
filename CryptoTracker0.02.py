import sqlite3 as lite

create_holdings_table = "CREATE TABLE Holdings(Coin_held TEXT, Amt_held REAL);"
insert_user_inputted_holdings = "INSERT INTO Holdings VALUES(?, ?);"
create_transactions_table = "CREATE TABLE Transactions(Date_pur NUMERIC, Coin_pur TEXT, Amt_coin_pur REAL, Price_per_coin REAL, Coin_sold TEXT, Amt_coin_sold REAL, Exchange_of_trx TEXT, If_sold TEXT, Cur_held_loc TEXT, Amt_sold REAL, Date_sold NUMERIC);"
insert_CBP_fills = "INSERT INTO Transactions (Date_pur, Coin_pur, Amt_coin_pur, Price_per_coin, Coin_sold, Amt_coin_sold, Exchange_of_trx) VALUES(?, ?, ?, ?, ?, ?, ?);"
update_holdings_from_CBP_fills = "UPDATE Holdings SET Amt_held = ? WHERE Coin_held = ?"
get_amt_by_coin = "SELECT Amt_held FROM Holdings WHERE Coin_held = ?"
add_0_holding = "INSERT INTO Holdings VALUES(?, ?);"

def create_db():
    name_database = input("What would you like to name your database? (use .db extension): ")
    con = lite.connect(name_database) #DB that stores user data
    cur = con.cursor()

    with con:     
        cur.execute(create_transactions_table)
        cur.execute(create_holdings_table)
        '''for i in range(len(fills_CBP)):
            if fills_CBP[i][3] == "BUY":
                cur.execute(insert_CBP_fills, (fills_CBP[i][4], fills_CBP[i][6], float(fills_CBP[i][5]), float(fills_CBP[i][7]), fills_CBP[i][10], float(fills_CBP[i][9]), "CBP"))
            elif fills_CBP[i][3] == "SELL":
                cur.execute(insert_CBP_fills, (fills_CBP[i][4], fills_CBP[i][10], float(fills_CBP[i][9]), 1/(float(fills_CBP[i][7])), fills_CBP[i][6], float(fills_CBP[i][5]), "CBP"))
        '''
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

def user_import_transactions_CBP():
    user_fills_csv = input("Enter the filename of the CBP fills file (ENTER for default fills.csv): ") or 'fills.csv'
    with open(user_fills_csv, 'r') as cbpinfile: #CBP csv file (fills.csv)
        transactions = []
        for row in cbpinfile:
            cells = row.split(',')
            transactions.append(cells) #After for loop, the list transactions now has all the data from the csv
    transactions = transactions[1:] #Removes the csv file's headers from the list
    cbpinfile.close()
    return transactions
    
def add_holdings_by_hand(db):
    con = lite.connect(db) #DB that stores user data
    user_new_holdings = user_input_holdings()
    cur = con.cursor()

    with con:
        for i in range(len(user_new_holdings)):
            cur.execute(insert_user_inputted_holdings, (user_new_holdings[i][0], user_new_holdings[i][1]))
    con.commit()

def update_transactions_and_holdings_with_CBP_fills(name_database):
    con = lite.connect(name_database)
    cur = con.cursor()
    fills_CBP = user_import_transactions_CBP()
    with con:     
        for i in range(len(fills_CBP)):
            con.commit()
            if fills_CBP[i][3] == "BUY":
                amt_held = (get_cur_holdings(name_database, fills_CBP[i][6]))
                cur.execute(update_holdings_from_CBP_fills, ((amt_held + float(fills_CBP[i][5])), fills_CBP[i][6]))
                cur.execute(insert_CBP_fills, (fills_CBP[i][4], fills_CBP[i][6], float(fills_CBP[i][5]), float(fills_CBP[i][7]), fills_CBP[i][10], float(fills_CBP[i][9]), "CBP"))
            elif fills_CBP[i][3] == "SELL":
                amt_held = float(get_cur_holdings(name_database, fills_CBP[i][10]))
                cur.execute(update_holdings_from_CBP_fills, ((amt_held - float(fills_CBP[i][9])), fills_CBP[i][10]))
                cur.execute(insert_CBP_fills, (fills_CBP[i][4], fills_CBP[i][10], float(fills_CBP[i][9]), 1/(float(fills_CBP[i][7])), fills_CBP[i][6], float(fills_CBP[i][5]), "CBP"))
    
def get_cur_holdings(name_database, coin):
    con = lite.connect(name_database)
    cur = con.cursor()
    with con:
        held = cur.execute(get_amt_by_coin, (coin,)).fetchall()
    try:
        held = held.pop()
    except:
        cur.execute(add_0_holding, (coin, 0.0))
        con.commit()
        held = [(0.0)]
    amt_held = float(held[0])
    return amt_held

def main():
    user_database_name = create_db()
    #add_holdings_by_hand(user_database_name)
    update_transactions_and_holdings_with_CBP_fills(user_database_name)
    
main()
