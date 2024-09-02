# -*- coding: utf-8 -*-
"""
Created on Sun Sep  1 11:55:55 2024

@author: ck
"""

import streamlit as st
import pandas as pd
from io import BytesIO

# Step 1: Read the excel file for fuel transaction
st.sidebar.title("Fuel Efficiency Calculator")
uploaded_file = st.sidebar.file_uploader("Upload your excel file", type="xlsx")

# Step 2: Create an empty field to allow user to insert fuel efficiency factor in KM/Liter
efficiency_factor = st.sidebar.number_input("Insert Fuel Efficiency factor in KM/Liter", min_value=0.1, step=0.1)

if uploaded_file is not None:
    # Load the data into a DataFrame
    df = pd.read_excel(uploaded_file)
    
    # Remove the timestamp from TransactionDate, keeping only the date
    df['TransactionDate'] = pd.to_datetime(df['TransactionDate']).dt.strftime('%d-%m-%Y')

    # Step 3: Group by VehicleRegistrationNo and sort by TransactionDate
    df.sort_values(by=["VehicleRegistrationNo", "TransactionDate"], inplace=True)

    # Initialize columns for new data
    df['Initial Odometer'] = None
    df['Final Odometer'] = None
    df['Distance'] = None
    df['Rolling Quantity'] = None
    df['Fuel Efficiency'] = None
    df['Fuel Usage'] = None
    df['Usage Type'] = None
    
    # Step 4 to 12: Process each VehicleRegistrationNo and TransactionDate
    for vehicle, vehicle_df in df.groupby("VehicleRegistrationNo"):
        initial_odometer = None
        initial_quantity = 0
        rolling_quantity = 0
        final_odometer = None
        
        # Sort transactions for each vehicle by TransactionDate
        vehicle_df = vehicle_df.sort_values(by="TransactionDate")

        for index, row in vehicle_df.iterrows():
            if row['Capacity'] == 'Y':
                if initial_odometer is not None and row['Odometer'] > initial_odometer:
                    # Calculate Distance and Fuel Efficiency
                    final_odometer = row['Odometer']
                    distance = final_odometer - initial_odometer

                    if distance > 0:  # Ensure valid distance
                        fuel_efficiency = distance / rolling_quantity

                        # Calculate Fuel Usage
                        fuel_usage = (distance / efficiency_factor) - rolling_quantity
                        usage_type = "Saving" if fuel_usage >= 0 else "Excessive Use"
                    
                        # Update the DataFrame with calculated values
                        df.at[index, 'Initial Odometer'] = initial_odometer
                        df.at[index, 'Final Odometer'] = final_odometer
                        df.at[index, 'Distance'] = distance
                        df.at[index, 'Rolling Quantity'] = rolling_quantity
                        df.at[index, 'Fuel Efficiency'] = fuel_efficiency
                        df.at[index, 'Fuel Usage'] = fuel_usage
                        df.at[index, 'Usage Type'] = usage_type

                # Reset Initial Odometer and Initial Quantity after a valid calculation
                initial_odometer = row['Odometer']
                initial_quantity = row['Quantity']
                rolling_quantity = initial_quantity
            else:
                # Accumulate Quantity for transactions where Capacity = 'N'
                rolling_quantity += row['Quantity']
    
    # Display the modified DataFrame in the main window
    st.write("Fuel Efficiency Results")
    st.dataframe(df)
    
    # Option to download the modified DataFrame as an Excel file
    def to_excel(df):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        writer.save()
        processed_data = output.getvalue()
        return processed_data
    
    excel_data = to_excel(df)
    
    st.download_button(
        label="Download Output File as Excel",
        data=excel_data,
        file_name='fuel_efficiency_results.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
