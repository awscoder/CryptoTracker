# CBPBookeeping
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

*Next steps*
1) Increase efficiency (looking at pulling data from db instead of fills after fills has been imported (84-96)
2) This will also helpwith importing other files down the line
3) Eventually a better interface
4) The ability to display portfolio
5) Track cpc
6) Make graphs
