# CryptoTracker
A rough shot at an early version of open-source crypto accounting software for Coinbase Pro (CBP) users (written in Python)
To view the database I recommend DB Browser (https://sqlitebrowser.org/dl/)

!!!NOTE!!! in the current verison of this code, the results are only accurate if you only use CBP to buy and
sell crypto and have never added or withdrawn crypto via the blockchain.

*To automatically generate a database of your past transactions and your current holdings*

1) Download fills.csv from your CBP account (in the documents section) and place it in the same directory as this python file.
2) *optional*: open the csv file in a spreadsheet viewer and sort by date. (CBP sorts by tx ID by default)
3) Run the program in a python shell or IDE
4) Input the name for the program to call its database (e.g. myCPBdatabase.db). *Ensure you use the .db extension*
5) If you have fills.csv in the same directory as this code, hit enter, if not enter the filepath.
6) Wait approximately 1 minute
7) Use DB browser to open your database and you can see your holdings and transaction history.

*For generic import of any transactions make or download a csv file and follow the exact formatting provided*
1) Column 1 should have BUY and SELL to indicate whether the order was a buy or sell order (be sure to capitalize)
2) Column 2 should have the date in the **dd-mm-yyyy** format for CoinGecko price requests to function
3) Column 3 should have the coin acquired
4) Column 4 should have the amount purchases of the coin from column 3
5) Column 5 should have the price per coin (coin purchased/ coin sold (e.g. BTC/USD) 
6) Column 6 should have the coin sold (normally USD if you are buying in fiat and the cryptocurrency if you are selling crypto)
7) Column 7 should have the amount sold of the coin from column 6
8) Leave your headings as the top row in your csv file. THE PROGRAM REMOVES THE FIRST LINE AS IT ASSUMES IT IS HEADINGS! You will loose a transaction if you have no header row.
9) Check your file for any irregularites such as negatives or newline characters (\n) as some exchanges add these

**Here is an example of a generic table with example data formatted correctly**
![image](https://user-images.githubusercontent.com/38738303/110228685-9d25ef00-7ec8-11eb-9642-c54bf17bdb00.png)


*Next steps*
~~1) Generic csv importer~~
2) Eventually a better interface
3) The ability to display portfolio
4) Track cost-per-coin
5) Make graphs
6) Calculate FIFO capital gains/losses
