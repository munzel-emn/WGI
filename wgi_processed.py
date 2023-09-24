import pandas as pd


def process_files(file1_name, file2_name, file3_name):
    # Load the three Excel files
    file1 = pd.read_excel(file1_name)
    file2 = pd.read_excel(file2_name)
    file3 = pd.read_excel(file3_name)

    # Rename "WGI Date" column to "Date" in file1
    file1.rename(columns={'WGI Date': 'Date'}, inplace=True)

    # Delete rows in file1 where "Date" is not a valid date
    file1['Date'] = pd.to_datetime(file1['Date'], errors='coerce')
    file1 = file1.dropna(subset=['Date'])

    # Rename "Container Number" column to "Container #" in file1 and file3
    file1.rename(columns={'Container Number': 'Container #'}, inplace=True)
    file3.rename(columns={'Container Number': 'Container #'}, inplace=True)

    # Print the first 10 rows of each file
    print("File 1 - First 15 rows:")
    print(file1.head(15))
    print("\nFile 2 - First 10 rows:")
    print(file2.head(10))
    print("\nFile 3 - First 10 rows:")
    print(file3.head(10))

    # Check and filter rows in the first file without dates
    file1 = file1[file1['Date'].notna()]

    # Create missing columns if they don't exist
    missing_columns = ['Consignor', 'Type', 'Depot', 'Principal']
    for col in missing_columns:
        if col not in file1.columns:
            file1[col] = None

    # Rearrange the columns in the desired order
    desired_order = ['Container #', 'EIR#', 'Consignor', 'Type', 'Date', 'Depot', 'Empty', 'Principal']
    file1 = file1[desired_order]

    # Set values in the 'Depot' and 'Type' columns
    file1['Depot'] = 'LMW'
    file1['Type'] = 'WGI'

    # Check and filter container numbers in the first file against the second file
    common_containers = set(file1['Container #']) & set(file2['Container #'])
    file1 = file1[~file1['Container #'].isin(common_containers)]

    # Find consignor codes in the third file based on container numbers from the first file
    consignor_codes = []
    for container in file1['Container #']:
        matching_row = file3[file3['Container #'] == container]
        if not matching_row.empty:
            consignor_codes.append(matching_row.iloc[0]['Consignor Code'])
        else:
            consignor_codes.append(None)

    # Add the consignor codes to the first file
    file1['Consignor'] = consignor_codes

    # Update the 'Principal' column based on conditions
    condition = file1['Container #'].str.startswith(('CELU', 'CELR', 'TKKU', 'TRIU'))
    file1.loc[condition, 'Principal'] = 'CELGEN'

    # Update the 'Principal' column based on conditions in 'Consignor' column
    consigned_to_swires = file1['Consignor'].isin(['SWIMTS', 'SWIIMP', 'SWILAE'])
    file1.loc[consigned_to_swires, 'Principal'] = 'SWIRES'

    # Update the 'Principal' column based on conditions in 'Consignor' column
    consigned_to_carpsa = file1['Consignor'].isin(['CARPSA'])
    file1.loc[consigned_to_carpsa, 'Principal'] = 'CARPSA'

    # Print the modified first file
    print("\nModified File 1:")
    print(file1.head(10))

    # Save the modified DataFrame to a CSV file
    modified_filename = file1_name.replace('.xlsx', '_modified.csv')
    file1.to_csv(modified_filename, index=False)
    print(f"Modified DataFrame saved as {modified_filename}")


# Prompt the user for filenames and process the files
file1_input = input("Enter the filename for File 1: ")
file2_input = input("Enter the filename for File 2: ")
file3_input = input("Enter the filename for File 3: ")

process_files(file1_input, file2_input, file3_input)