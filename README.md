# Analysis-of-the-Berlin-rental-market
At first I took a web-site with rental advertisements in Berlin (https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-mieten), parsed it and got all the current advertisements. Then all the new advertisements are saved to SQL database. With that 2 optional arguments can be used:
'''
-- path - the path to db file where to save the data
-- if_exists - to append data to ads stored from previous days or to replace the data in database
'''
Then I analyzed the data, built plots. Then the Ridge linear model was built to forecast the monthly rent of an apartment by other indicators.
