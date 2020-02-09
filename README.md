# Analysis-of-the-Berlin-rental-market
At first I took a web-site with rental advertisements in Berlin (https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten), parsed it and got all the current advertisements. Then all the new advertisements are saved to SQL database.These steps are done py script ```ads_data.py```. By saving to SQL database 2 optional arguments can be used:
```
--path - the path to db file where to save the data (default = "immobilienscout24.db")
--if_exists - to append data to ads stored from previous days or to replace the data in database
```
Then I have analyzed the data and have built plots in ```Berlin_rental_market_analysis.ipynb```. Then the Ridge linear model was built there to forecast the monthly rent of an apartment by other indicators.
