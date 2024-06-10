import pandas as pd

path =r'C:\All_In_One_iSell\InputData\Rateshop\11_Apr_2024'

rdata= pd.read_csv(path+'\DEDZD_RateShop.csv')

hyatt_king_data = rdata[(rdata['Hotel Name'] == 'Hyatt Regency Dehradun Resort and Spa') &
                        (rdata['MealInclusionType'] == 'Complimentary Breakfast') &
                        (rdata['Room Type Description'] == 'Hyatt King Room')]

hotel_name = 'DEDZD'

# Generate the Excel file name
excel_file_name = hotel_name.replace(" ", "_") + "_Rateshop.xlsx"

# Define the full path for saving the Excel file
output_path = r"C:\All_In_One_iSell\InputData\\" + excel_file_name

# Save the filtered data to an Excel file
#hyatt_king_data.to_excel(output_path, index=False)


fairfield_data = rdata[(rdata['Hotel Name'] == 'Fairfield by Marriott Dehradun') &
                       (rdata['MealInclusionType'] == 'No meals included') &
                       (rdata['Room Type Description'] == 'Standard  King Room')]

# Define the hotel name for file naming
hotel_name = "Fairfield by Marriott Dehradun"

# Generate the Excel file name
excel_file_name = hotel_name.replace(" ", "_") + "_Rateshop.xlsx"

# Define the full path for saving the Excel file
output_path = r"C:\All_In_One_iSell\InputData\\" + excel_file_name

# Save the filtered data to an Excel file
# fairfield_data.to_excel(output_path, index=False)


# Filter the DataFrame to include only data for the hotel "DEDZD"
# and specific MealInclusionType and Room Type Description


dedzd_data = rdata[(rdata['Hotel Name'] == 'DEDZD') &
                   (rdata['MealInclusionType'] == 'Complimentary Breakfast') &
                   (rdata['Room Type Description'] == 'Standard Twin Room')]

# Define the hotel name for file naming
hotel_name = "DEDZD"

# Generate the Excel file name
excel_file_name = hotel_name + "_Rateshop.xlsx"

# Define the full path for saving the Excel file
output_path = r"C:\All_In_One_iSell\InputData\\" + excel_file_name

# Save the filtered data to an Excel file
# dedzd_data.to_excel(output_path, index=False)

ramada_data = rdata[(rdata['Hotel Name'] == 'Ramada by Wyndham Dehradun') &
                    (rdata['Room Type Description'] == 'Deluxe 1 King Bed Smoking Room') &
                    (rdata['Rate Type'] == 'Fully Restricted')]

# Define the hotel name for file naming
hotel_name = "Ramada by Wyndham Dehradun"

# Generate the Excel file name
excel_file_name = hotel_name.replace(" ", "_") + "_Rateshop.xlsx"

# Define the full path for saving the Excel file
output_path = r"C:\All_In_One_iSell\InputData\\" + excel_file_name

# Save the filtered data to an Excel file
# ramada_data.to_excel(output_path, index=False)


# Filter the DataFrame to include only data for the hotel "Fortune Resort Grace"
# and specific MealInclusionType, Room Type Description, and Rate Type
fortune_data = rdata[(rdata['Hotel Name'] == 'Fortune Resort Grace') &
                     (rdata['MealInclusionType'] == 'Breakfast Included') &
                     (rdata['Room Type Description'] == 'Deluxe Room') &
                     (rdata['Rate Type'] == 'Semi Restricted')]

# Define the hotel name for file naming
hotel_name = "Fortune Resort Grace"

# Generate the Excel file name
excel_file_name = hotel_name.replace(" ", "_") + "_Rateshop.xlsx"

# Define the full path for saving the Excel file
output_path = r"C:\All_In_One_iSell\InputData\\" + excel_file_name

# Save the filtered data to an Excel file
fortune_data.to_excel(output_path, index=False)


print(rdata.head())