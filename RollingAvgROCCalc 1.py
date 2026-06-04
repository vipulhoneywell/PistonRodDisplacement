# import pandas as pd

# def calculate_latest_metrics(file_path):
#     # 1. Load the Excel file
#     df = pd.read_excel(file_path)
    
#     # 2. Clean and sort data by time
#     df['Time'] = pd.to_datetime(df['Time'])
#     df = df.sort_values('Time').reset_index(drop=True)
    
#     # 3. Get the latest row information
#     latest_row = df.iloc[-1]
#     latest_time = latest_row['Time']
#     latest_val = latest_row['365KBVZT101']
#     # running_status = latest_row['running_status']
#     # --- 2-Hour Rolling Average ---
#     # Filter data to only include the last 2 hours from the latest Time
    
#     rolling_avg_hr = 2
#     two_hours_ago = latest_time - pd.Timedelta(hours=rolling_avg_hr)
#     df_2hr = df[(df['Time'] >= two_hours_ago) & (df['Time'] <= latest_time)]
#     rolling_avg = df_2hr['365KBVZT101'].mean()
    
#     # --- 12-Hour Rate of Change (ROC) ---
#     # Find the data point exactly 12 hours prior (or the closest available one before it)
#     ROC_hr = 12
#     twelve_hours_ago = latest_time - pd.Timedelta(hours=ROC_hr)
#     df_12hr_prior = df[df['Time'] <= twelve_hours_ago]
    
#     if not df_12hr_prior.empty:
#         # Get the closest value to the 12-hour mark
#         val_12hr = df_12hr_prior.iloc[-1]['365KBVZT101']
        
#         # Calculate ROC using your formula: ((12val - current) / 12val) * 100
#         if val_12hr != 0:
#             roc = ((latest_val - val_12hr) / val_12hr) * 100
#         else:
#             roc = None  # Prevent division by zero
#     else:
#         roc = None  # Not enough historical data (less than 12 hours of data)
#         val_12hr = None

#     # 4. Print results
#     print(f"Latest Timestamp: {latest_time}")
#     print(f"Latest Value: {latest_val}")
#     print(f"2-Hour Rolling Avg: {rolling_avg:.2f}")
#     print(f"12-Hour Prior Value: {val_12hr}")
#     print(f"12-Hour ROC: {f'{roc:.2f}%' if roc is not None else 'N/A'}")

# # Example Usage:
# calculate_latest_metrics("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")

# import pandas as pd

# def calculate_time_series_metrics(file_path):
#     df = pd.read_excel(file_path)

#     # ✅ Convert to datetime (force bad values → NaT)
#     df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

#     # ✅ DEBUG: Check NaT count
#     print("NaT count before cleaning:", df['Time'].isna().sum())

#     # ✅ Drop all NaT rows
#     df = df.dropna(subset=['Time'])

#     # ✅ Sort BEFORE setting index
#     df = df.sort_values('Time')

#     # ✅ Remove duplicates
#     df = df.drop_duplicates(subset='Time')

#     # ✅ Set index
#     df.set_index('Time', inplace=True)

#     # ✅ FINAL SAFETY CHECK (VERY IMPORTANT)
#     print("Any NaT in index:", df.index.isna().any())

#     # ✅ If still True, force remove
#     df = df[~df.index.isna()]

#     # ✅ Ensure strictly increasing time
#     df = df.sort_index()

#     # ----------------------------
#     # ✅ Rolling Mean (2 Hour)
#     # ----------------------------
#     df['Rolling_Mean_2H'] = df['365KBVZT101'].rolling('2H').mean()

#     # ----------------------------
#     # ✅ ROC 12 Hour
#     # ----------------------------
#     df['Value_12hr_ago'] = df['365KBVZT101'].shift(freq='12H')

#     df['ROC_12H'] = ((df['365KBVZT101'] - df['Value_12hr_ago']) / df['365KBVZT101']) * 100

#     return df.reset_index()


# # Run
# result_df = calculate_time_series_metrics("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")
# print(result_df.head())
# result_df.to_csv("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/OutputROC.csv")
# import pandas as pd

# def calculate_latest_metrics(file_path):

#     # -------------------------------
#     # 1. Load Excel file
#     # -------------------------------
#     df = pd.read_excel(file_path, engine='openpyxl')

#     # -------------------------------
#     # 2. Keep only required columns
#     # -------------------------------
#     df = df[['Time', '365KBVZT101']]

#     # -------------------------------
#     # 3. Convert Time column properly
#     # -------------------------------
#     df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')

#     # Remove bad rows (fixes NaT issue)
#     df = df.dropna(subset=['Time', '365KBVZT101'])

#     # Sort by time
#     df = df.sort_values('Time').reset_index(drop=True)

#     # -------------------------------
#     # 4. Get latest values
#     # -------------------------------
#     latest_row = df.iloc[-1]
#     latest_time = latest_row['Time']
#     latest_val = latest_row['365KBVZT101']

#     # -------------------------------
#     # 5. 2-Hour Rolling Average
#     # -------------------------------
#     df = df.set_index('Time')

#     rolling_avg = df['365KBVZT101'].rolling('2h').mean().iloc[-1]

#     # -------------------------------
#     # 6. 12-Hour Rate of Change
#     # -------------------------------
#     twelve_hours_ago = latest_time - pd.Timedelta(hours=12)

#     df_reset = df.reset_index()

#     df_12hr = df_reset[df_reset['Time'] <= twelve_hours_ago]

#     if not df_12hr.empty:
#         val_12hr = df_12hr.iloc[-1]['365KBVZT101']

#         if val_12hr != 0:
#             roc = ((latest_val - val_12hr) / val_12hr * 100)
#         else:
#             roc = None
#     else:
#         val_12hr = None
#         roc = None

#     # -------------------------------
#     # 7. Format time (Windows-safe)
#     # -------------------------------
#     formatted_time = (
#         f"{latest_time.day}/{latest_time.month}/{str(latest_time.year)[-2:]} "
#         f"{latest_time.strftime('%I:%M %p').lstrip('0')}"
#     )

#     # -------------------------------
#     # 8. Print output
#     # -------------------------------
#     print(f"Latest Time: {formatted_time}")
#     print(f"Latest Value: {latest_val:.2f}")
#     print(f"2-Hour Rolling Avg: {rolling_avg:.2f}")

#     if val_12hr is not None:
#         print(f"12-Hour Prior Value: {val_12hr:.2f}")
#         print(f"12-Hour ROC: {roc:.2f}%")
#     else:
#         print("12-Hour Prior Value: N/A")
#         print("12-Hour ROC: N/A")


# # ✅ Run the function
# calculate_latest_metrics(
#     "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
# )




# import pandas as pd

# def calculate_excel_logic(file_path):

#     # -------------------------------
#     # 1. Load & clean data
#     # -------------------------------
#     df = pd.read_excel(file_path, engine='openpyxl')

#     df = df[['Time', '365KBVZT101']]
#     df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')

#     df = df.dropna(subset=['Time', '365KBVZT101'])
#     df = df.sort_values('Time').reset_index(drop=True)

#     # Rename for simplicity
#     df.rename(columns={'365KBVZT101': 'Value'}, inplace=True)

#     # -------------------------------
#     # Column B → Rolling Average (38 rows)
#     # Excel: =AVERAGE(B2:B39)
#     # -------------------------------
#     window_size = 38

#     df['Rolling_Avg'] = (
#         df['Value']
#         .rolling(window=window_size, min_periods=window_size)
#         .mean()
#     )

#     # -------------------------------
#     # Column C → (Current - value 238 rows before) / old * 100
#     # Excel: =(B240 - B2)
#     # -------------------------------
#     shift_rows = 238

#     df['Value_238_rows_before'] = df['Value'].shift(shift_rows)

#     df['ROC_C'] = (
#         (df['Value'] - df['Value_238_rows_before'])
#         / df['Value_238_rows_before']
#     ) * 100

#     # -------------------------------
#     # Column D → (C - B) / C * 100
#     # -------------------------------
#     df['ROC_D'] = (
#         (df['ROC_C'] - df['Value'])
#         / df['ROC_C']
#     ) * 100

#     # -------------------------------
#     # 3. Save output
#     # -------------------------------
#     output_file = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/excel_logic_output.xlsx"
#     df.to_excel(output_file, index=False)

#     print("Output saved to:", output_file)


# # ✅ Run
# calculate_excel_logic("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")

# import pandas as pd

# def calculate_latest_metrics(file_path):
#     # 1. Load the Excel file
#     df = pd.read_excel(file_path)

#     # 2. Clean and sort data
#     df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
#     df = df.dropna(subset=['Time', '365KBVZT101'])
#     df = df.sort_values('Time').reset_index(drop=True)

#     # 3. Get latest row
#     latest_row = df.iloc[-1]
#     latest_time = latest_row['Time']
#     latest_val = latest_row['365KBVZT101']

#     # -------------------------------
#     # ✅ 2-HOUR ROLLING AVG
#     # -------------------------------
#     two_hours_ago = latest_time - pd.Timedelta(hours=2)

#     df_2hr = df[
#         (df['Time'] >= two_hours_ago) &
#         (df['Time'] <= latest_time)
#     ]

#     rolling_avg = df_2hr['365KBVZT101'].mean()

#     # -------------------------------
#     # ✅ 12-HOUR LOOKBACK (WITH TOLERANCE)
#     # -------------------------------
#     twelve_hours_ago = latest_time - pd.Timedelta(hours=12)

#     # Find closest value BEFORE target time
#     df_prior = df[df['Time'] <= twelve_hours_ago]

#     if not df_prior.empty:
#         val_12hr = df_prior.iloc[-1]['365KBVZT101']
#         time_12hr = df_prior.iloc[-1]['Time']

#         # ✅ Apply tolerance (10 minutes)
#         if (twelve_hours_ago - time_12hr) <= pd.Timedelta(minutes=10):

#             # ✅ ROC: (C - B) / C * 100
#             if latest_val != 0:
#                 roc = ((latest_val - val_12hr) / latest_val * 100)
#             else:
#                 roc = None
#         else:
#             # Too far → reject value
#             val_12hr = None
#             roc = None
#     else:
#         val_12hr = None
#         roc = None

#     # -------------------------------
#     # ✅ Output
#     # -------------------------------
#     print(f"Latest Timestamp: {latest_time}")
#     print(f"Latest Value: {latest_val}")
#     print(f"2-Hour Rolling Avg: {rolling_avg:.2f}")
#     print(f"12-Hour Prior Value: {val_12hr}")
#     print(f"12-Hour ROC: {f'{roc:.2f}%' if roc is not None else 'N/A'}")


# # ✅ Run
# calculate_latest_metrics(
#     "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
# )


# import pandas as pd

# def calculate_latest_metrics(file_path):
    
#     # 1. Load data
#     df = pd.read_excel(file_path)
    
#     # 2. Preprocessing
#     df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
#     df = df.dropna(subset=['Time', '365KBVZT101'])
#     df = df.sort_values('Time').reset_index(drop=True)
    
#     # 3. Latest values
#     latest_row = df.iloc[-1]
#     latest_time = latest_row['Time']
#     latest_val = latest_row['365KBVZT101']
    
#     # ---------------------------------------------------
#     # 2-Hour Rolling Average (latest window)
#     # ---------------------------------------------------
#     rolling_avg_hr = 2
#     two_hours_ago = latest_time - pd.Timedelta(hours=rolling_avg_hr)
    
#     df_2hr = df[(df['Time'] >= two_hours_ago) & (df['Time'] <= latest_time)]
#     rolling_avg = df_2hr['365KBVZT101'].mean()
    
#     # ---------------------------------------------------
#     # 12-Hour Rate of Change (ROC)
#     # ---------------------------------------------------
#     ROC_hr = 12
#     twelve_hours_ago = latest_time - pd.Timedelta(hours=ROC_hr)
    
#     df_12hr_prior = df[df['Time'] <= twelve_hours_ago]
    
#     val_12hr = None
#     roc = None
    
#     if not df_12hr_prior.empty:
#         val_12hr = df_12hr_prior.iloc[-1]['365KBVZT101']
        
#         if pd.notna(val_12hr) and val_12hr != 0:
#             # ROC = ((current - past) / past) * 100
#             roc = ((latest_val - val_12hr) / val_12hr) * 100
    
#     # ---------------------------------------------------
#     # Output
#     # ---------------------------------------------------
#     print(f"Latest Timestamp: {latest_time}")
#     print(f"Latest Value: {latest_val}")
#     print(f"2-Hour Rolling Avg: {rolling_avg:.2f}")
#     print(f"12-Hour Prior Value: {val_12hr}")
    
#     if roc is not None:
#         print(f"12-Hour ROC: {roc:.2f}%")
#     else:
#         print("12-Hour ROC: N/A")


# # Example
# calculate_latest_metrics("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")

# import pandas as pd

# def calculate_all_metrics(file_path):
    
#     # Load data
#     df = pd.read_excel(file_path)
    
#     # Clean
#     df['Time'] = pd.to_datetime(df['Time'])
#     df = df.sort_values('Time')
    
#     # Set index for time-based operations
#     df = df.set_index('Time')

#     # ---------------------------------------------------
#     # 1. 2-Hour Rolling Average (for ALL rows)
#     # ---------------------------------------------------
#     df['rolling_2h'] = df['365KBVZT101'].rolling('2H').mean()

#     # ---------------------------------------------------
#     # 2. 12-Hour ROC (for ALL rows)
#     # ---------------------------------------------------
#     df['value_12h_ago'] = df['365KBVZT101'].shift(freq='12H')

#     df['roc_12h'] = (
#         (df['365KBVZT101'] - df['value_12h_ago'])
#         / df['value_12h_ago']
#     ) * 100

#     # ---------------------------------------------------
#     # Reset index (optional)
#     # ---------------------------------------------------
#     df = df.reset_index()

#     print(df.tail(10))  # show last few rows

#     return df


# # Run
# df_result = calculate_all_metrics("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")

# import pandas as pd
# import numpy as np

# def calculate_metrics_from_12hr_data(file_path):

#     # ---------------------------
#     # 1. Load data
#     # ---------------------------
#     df = pd.read_excel(file_path, engine='openpyxl')

#     df = df[['Time', '365KBVZT101']]
#     df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

#     df = df.dropna()
#     df = df.sort_values('Time').reset_index(drop=True)

#     # Rename for simplicity
#     df.rename(columns={'365KBVZT101': 'Value'}, inplace=True)

#     # ---------------------------
#     # 2. Rolling Avg (2 hours)
#     # ---------------------------
#     df = df.set_index('Time')
#     df['Rolling_2hr'] = df['Value'].rolling('2H').mean()
#     df = df.reset_index()

#     # ---------------------------
#     # 3. 12-hour ROC logic
#     # (first timestamp vs last)
#     # ---------------------------
#     start_time = df.iloc[0]['Time']
#     end_time = df.iloc[-1]['Time']

#     start_value = df.iloc[0]['Value']
#     end_value = df.iloc[-1]['Value']

#     # Check if span >= 12 hours
#     time_diff = end_time - start_time

#     if time_diff >= pd.Timedelta(hours=12) and start_value != 0:
#         roc_12hr = ((end_value - start_value) / start_value) * 100
#     else:
#         roc_12hr = np.nan

#     # Assign ROC only to last row
#     df['ROC_12hr'] = np.nan
#     df.loc[df.index[-1], 'ROC_12hr'] = roc_12hr

#     # ---------------------------
#     # 4. Output
#     # ---------------------------
#     print("Start Time :", start_time)
#     print("End Time   :", end_time)
#     print("Start Value:", start_value)
#     print("End Value  :", end_value)
#     print(f"12hr ROC   : {roc_12hr:.2f}%")

#     # Save output
#     output_file = "ROC_output.xlsx"
#     df.to_excel(output_file, index=False)

#     print("✅ Output saved to:", output_file)

#     return df

# # ✅ RUN
# file_path = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
# df_result = calculate_metrics_from_12hr_data(file_path)



import pandas as pd
import numpy as np

def calculate_split_outputs(file_path, roc_hours=12):

    # ---------------------------
    # 1. Load data
    # ---------------------------
    df = pd.read_excel(file_path, engine='openpyxl')

    df = df[['Time', '365KBVZT101']]
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

    df = df.dropna()
    df = df.sort_values('Time').reset_index(drop=True)

    df.rename(columns={'365KBVZT101': 'Value'}, inplace=True)

    # ---------------------------
    # 2. 2-Hour Rolling List
    # ---------------------------
    df = df.set_index('Time')
    rolling_series = df['Value'].rolling('2H').mean()
    df = df.reset_index()

    rolling_list = rolling_series.tolist()

    # ---------------------------
    # 3. ROC using variable hours
    # ---------------------------
    start_time = df.iloc[0]['Time']
    end_time = df.iloc[-2]['Time']   # as per your logic

    start_value = df.iloc[0]['Value']
    end_value = df.iloc[-2]['Value']

    time_diff = end_time - start_time

    roc_list = [np.nan] * len(df)

    if time_diff >= pd.Timedelta(hours=roc_hours) and start_value != 0:
        roc_value = ((end_value - start_value) / start_value) * 100
        roc_list[-1] = roc_value

    # ---------------------------
    # 4. Attach to DataFrame
    # ---------------------------
    df['Rolling_2hr_List'] = rolling_list
    df['ROC_List'] = roc_list

    # ---------------------------
    # 5. Output
    # ---------------------------
    print(f"✅ ROC calculated for {roc_hours} hours")
    print(df.tail(5))

    # Save
    output_file = f"split_output_{roc_hours}hr.xlsx"
    df.to_excel(output_file, index=False)

    print("✅ Output saved:", output_file)

    return df, rolling_list, roc_list



# ✅ Run
# file_path = "ROC.xlsx"
file_path = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
df, rolling_list, roc_list = calculate_split_outputs(file_path)

# def calculate_split_outputs(file_path, roc_hours=12, rolling_hours = 2):

#     # ---------------------------
#     # 1. Load data
#     # ---------------------------
#     df = pd.read_excel(file_path, engine='openpyxl')

#     df = df[['Time', '365KBVZT101']]
#     df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

#     df = df.dropna()
#     df = df.sort_values('Time').reset_index(drop=True)

#     df.rename(columns={'365KBVZT101': 'Value'}, inplace=True)

#     # ---------------------------
#     # 2. 2-Hour Rolling List
#     # ---------------------------
#     df = df.set_index('Time')
#     rolling_series = df['Value'].rolling(f'{rolling_hours}H').mean()
#     df = df.reset_index()

#     rolling_list = rolling_series.tolist()

#     # ---------------------------
#     # 3. ROC using variable hours
#     # ---------------------------
#     start_time = df.iloc[0]['Time']
#     end_time = df.iloc[-2]['Time']   # as per your logic

#     start_value = df.iloc[0]['Value']
#     end_value = df.iloc[-2]['Value']

#     time_diff = end_time - start_time

#     roc_list = [np.nan] * len(df)

#     if time_diff >= pd.Timedelta(hours=roc_hours) and start_value != 0:
#         roc_value = ((end_value - start_value) / start_value) * 100
#         roc_list[-1] = roc_value

#     # ---------------------------
#     # 4. Attach to DataFrame
#     # ---------------------------
#     df['Rolling_2hr_List'] = rolling_list
#     df['ROC_List'] = roc_list

#     # ---------------------------
#     # 5. Output
#     # ---------------------------
#     print(f"✅ ROC calculated for {roc_hours} hours")
#     print(df.tail(5))

#     # Save
#     output_file = f"split_output_{roc_hours}hr.xlsx"
#     df.to_excel(output_file, index=False)

#     print("✅ Output saved:", output_file)

#     return df, rolling_list, roc_list

# ✅ Run
# file_path = "ROC.xlsx"
# file_path = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
# df, rolling_list, roc_list = calculate_split_outputs(file_path)
