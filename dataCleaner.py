#Clean up a CSV file with this script
import pandas as pd
import os
import re
import numpy as np

# Read in the data
data = pd.read_csv("/Users/couto/Desktop/DataCleaner/Resultados-MPSG-Open-Data-oct10-feb20.csv")
# Drop the rows with missing values
data = data.dropna()

# Fix the column names
# Go through the columns and ask the user to confirm the column names or provide a new name by user input       
# Then, go through the columns again to rename them
for col in data.columns:
    # Check if we're running interactively
    if os.isatty(0):
        # Ask the user for a new column name
        new_col = input(f'New name for column "{col}": ')
        # If the user provided a new name, rename the column
        if new_col != '':
            data = data.rename(columns={col: new_col})
    else:
        print(f"Warning: Can't rename column '{col}' because we're not running interactively")
data.to_csv('cleaned_data.csv', index=False)

# Go through the columns data and check if a char matches the typos dictionary
def fix_typos(data, columns=None):
  """
  This function corrects typos in a Pandas data frame.

  Args:
      data (pd.DataFrame): The data frame containing the typos.
      columns (list, optional): A list of column names to apply the corrections to. 
                                If None, corrections are applied to all string columns.

  Returns:
      pd.DataFrame: The data frame with corrected typos.
  """
  translation_table = str.maketrans(
      {ord('Û'): ord('o'), ord('¡'): ord('A'), ord('”'): ord('O'), ord('—'): ord('N'),
       ord('˙'): ord('u'), ord('…'): ord('E'), ord('Õ'): ord('I')}
  )

  # Apply corrections to all string columns by default
  if columns is None:
    columns = data.select_dtypes(include=[object]).columns

  for col in columns:
    if pd.api.types.is_string_dtype(data[col]):
      data[col] = data[col].str.translate(translation_table)
  
  return data

if os.isatty(0):
    # Ask the user if they want to check for typos in the data
    check_typos = input('Check for typos? (y/n): ')
    if check_typos.lower() == 'y':
        corrected_data = fix_typos(data)  # Apply corrections to all string columns

# Check for data types in the columns, print the column name and data type 
# and ask the user to confirm the data type or provide a new data type by user input
# if user wants to change the data type, remove the char that aren't part of the data type user selected
for col in data.columns:
    # Check if we're running interactively
    if os.isatty(0):
        # Ask the user if the data type is correct
        # The current data type should be displayed as the default new data type of the column
        # So the user can just press enter to keep the current data type or type a new data type
        print(f'{col} ({data[col].dtype})')
        new_dtype = input('New data type: ')
        # If the user provided a new data type, convert the column to that data type
        if new_dtype != '':
            try:
                data[col] = data[col].astype(new_dtype)
                # Remove characters that aren't part of the data type
                if new_dtype == 'int' or new_dtype == 'float' or new_dtype == 'int64' or new_dtype == 'float64':
                    data[col] = data[col].str.replace(r'\D', '', regex=True)
                elif new_dtype == 'str': # Only leave letters and spaces
                    # Remove special characters and put the strings in Uppercase
                    data[col] = data[col].str.replace(r'[^a-zA-Z\s]', '', regex=True)
                    data[col] = data[col].str.upper()


                    # Check if the strings are months in Spanish or English
                    # If they are, put them in Uppercase and remove special characters, just leaving the name of the month
                    months_english = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
                    months_spanish = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
                    months = months_english + months_spanish

                    # Create a regular expression pattern that matches any of the month names
                    pattern = '|'.join(months)
                    if data[col].str.upper().str.contains(pattern).any():
                        data[col] = data[col].str.upper().apply(lambda x: re.sub(f'(^.*?({pattern}).*?$)', r'\2', x) if re.search(f'(^.*?({pattern}).*?$)', x) else x)
            
            except ValueError:
                print(f"Error: Can't convert column '{col}' to data type '{new_dtype}'")

    else:
        print(f"Warning: Can't change data type of column '{col}' because we're not running interactively")

# Save the cleaned data to a new CSV file
data.to_csv('cleaned_data.csv', index=False)