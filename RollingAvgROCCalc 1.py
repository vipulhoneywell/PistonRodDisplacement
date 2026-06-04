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




import pandas as pd

def calculate_excel_logic(file_path):

    # -------------------------------
    # 1. Load & clean data
    # -------------------------------
    df = pd.read_excel(file_path, engine='openpyxl')

    df = df[['Time', '365KBVZT101']]
    df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')

    df = df.dropna(subset=['Time', '365KBVZT101'])
    df = df.sort_values('Time').reset_index(drop=True)

    # Rename for simplicity
    df.rename(columns={'365KBVZT101': 'Value'}, inplace=True)

    # -------------------------------
    # Column B → Rolling Average (38 rows)
    # Excel: =AVERAGE(B2:B39)
    # -------------------------------
    window_size = 38

    df['Rolling_Avg'] = (
        df['Value']
        .rolling(window=window_size, min_periods=window_size)
        .mean()
    )

    # -------------------------------
    # Column C → (Current - value 238 rows before) / old * 100
    # Excel: =(B240 - B2)
    # -------------------------------
    shift_rows = 238

    df['Value_238_rows_before'] = df['Value'].shift(shift_rows)

    df['ROC_C'] = (
        (df['Value'] - df['Value_238_rows_before'])
        / df['Value_238_rows_before']
    ) * 100

    # -------------------------------
    # Column D → (C - B) / C * 100
    # -------------------------------
    df['ROC_D'] = (
        (df['ROC_C'] - df['Value'])
        / df['ROC_C']
    ) * 100

    # -------------------------------
    # 3. Save output
    # -------------------------------
    output_file = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/excel_logic_output.xlsx"
    df.to_excel(output_file, index=False)

    print("Output saved to:", output_file)


# ✅ Run
calculate_excel_logic("C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx")

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