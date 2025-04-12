#Chad Laursen, Elias Fobert, Joseph Rather, Isaac Johnson, Alayna Smith
#IS303
#Runs a program that takes info from an excel sheet, cleans it, uploads it to postgres, runs queries, and prints a chat of summary stats

from sqlalchemy import create_engine, text
import pandas as pd
import psycopg2
import matplotlib.pyplot as plot

#Imports the data from the excel file, provides a list for data cleaning
filePath = "Retail_Sales_Data.xlsx"
productCategoriesDict = {
'Camera': 'Technology',
'Laptop': 'Technology',
'Gloves': 'Apparel',
'Smartphone': 'Technology',
'Watch': 'Accessories',
'Backpack': 'Accessories',
'Water Bottle': 'Household Items',
'T-shirt': 'Apparel',
'Notebook': 'Stationery',
'Sneakers': 'Apparel',
'Dress': 'Apparel',
'Scarf': 'Apparel',
'Pen': 'Stationery',
'Jeans': 'Apparel',
'Desk Lamp': 'Household Items',
'Umbrella': 'Accessories',
'Sunglasses': 'Accessories',
'Hat': 'Apparel',
'Headphones': 'Technology',
'Charger': 'Technology'}

#Estalishes a user input variable so we can initiate a while loop
userInput = 0

#Starts a while loop so we can stay in the program until we are done importing and returing summary stats
while userInput <= 3:

    #Collects input from user
    userInput = int(input(f"If you want to import data, enter 1. If you want to see summaries of stored data, enter 2. Enter any other value to exit the program: "))
    
    #Cleans and imports the data into postgres
    if userInput == 1:
        df = pd.read_excel(filePath)
        df[['First Name', 'Last Name']] = df['name'].str.split('_', expand=True)
        fName = df.pop('First Name')
        lName = df.pop('Last Name')
        df.drop('name', axis=1, inplace=True)
        df.insert(1, 'First Name', fName)
        df.insert(2, 'Last Name', lName)
        df['category'] = df['product'].map(productCategoriesDict).fillna(df['category'])
        engine = create_engine(f'postgresql+psycopg2://{'elias'}:{'cPccd45133!'}@{'localhost'}:{5432}/{'IS303'}')
        df.to_sql('sale', con=engine, if_exists='replace', index=True)
        print("You've imported the excel file into your postgres database.")
    
    #Runs a query and returns the categories that have been sold
    elif userInput == 2:
        print("The following are the categories that have been sold.")
        #Finds the database in postgres
        engine = create_engine(f'postgresql+psycopg2://{'elias'}:{'cPccd45133!'}@{'localhost'}:{5432}/{'IS303'}')

        #Runs the query
        query = """SELECT category 
        FROM sale
        GROUP BY category
        """

        #Stores the categories into a list and prints them out in a numbered list
        dfCategory = pd.read_sql_query(query, engine)
        categoryList = dfCategory['category'].tolist()
        for i, category in enumerate(categoryList, 1):
            print(f"{i}. {category}")
        
        #Collects input from a user to know which category to run analytics on
        repeat = True
        #Runs summary stats
        while repeat:
            try:
                summary = int(input("Please enter the number of the category you want to see summarized: "))
        
                if 1 <= summary <= len(categoryList): 
                    selectedCategory = categoryList[summary - 1]
                    #runs a query to pull sum, average, and count for a selected category
                    statsQuery = f"""
                        SELECT category, 
                            SUM(total_price) AS sum, 
                            AVG(total_price) AS avg, 
                            COUNT(quantity_sold) AS units
                        FROM sale
                        WHERE category = '{selectedCategory}'
                        GROUP BY category
                    """
                    #prints summary stats
                    dfStats = pd.read_sql_query(statsQuery, engine)
                    totalSales = dfStats.loc[0, 'sum']
                    averageSales = dfStats.loc[0, 'avg']
                    unitsSold = dfStats.loc[0, 'units']
                    print(f"\nSummary for {selectedCategory}:")
                    print(f"Total Sales: ${totalSales:,.2f}")
                    print(f"Average Sale: ${averageSales:,.2f}")
                    print(f"Units Sold: {unitsSold}")

                    #runs a query that pulls necessary info for the bar chart
                    chartQuery = f'''SELECT product, 
                            SUM(total_price) AS sum
                            FROM sale
                            WHERE category = '{selectedCategory}'
                            GROUP BY product
                            '''
                    
                    #saves the info into a pd dataframe and prints the plot
                    dfChart = pd.read_sql_query(chartQuery, engine)
                    dfChart.plot(kind='bar')
                    plot.title(f"Total Sales in {selectedCategory}")
                    plot.xlabel("Product")
                    plot.ylabel("Total Sales")
                    plot.xticks(ticks=range(len(dfChart)), labels=dfChart['product'], rotation=45)
                    plot.show()
                    
                    #repeats until the user is done
                    doAgain = input("Would you like to run statistics on another sales category? (yes/no): ").strip().lower()
                    if doAgain != "yes":
                        repeat = False
                else:
                    print("Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    #ends the program
    else:
        print("Closing the program.")
        break