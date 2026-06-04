



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

