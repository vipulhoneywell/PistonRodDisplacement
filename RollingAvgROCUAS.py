

"""
Author : Niharika / Vipul
Version: = 0.0
Last Update Date: 30-08-2025
 
"""
 
#UASName: PistonRodDisplacement_ROC_Calc
#UASDisplayName: PistonRodDisplacement_ROC_Calc
#UASDescription: PistonRodDisplacement_ROC_Calc
 
# UASInput: RunningStatus | Double
# UASInput: ROC_Hours | Double
# UASInput: Rolling_Hours | Double
# UASInput: STG_1_CYL_2_PRD_DISP | Double
# UASInput: STG_1_CYL_1_PRD_DISP | Double
 
 
# UASOutput: OutputStatus | String
# UASOutput: STG_1_CYL_1_ROLL_AVG | Double
# UASOutput: STG_1_CYL_1_ROC_DEV | Double
# UASOutput: STG_1_CYL_1_ROC_ABS | Double
# UASOutput: STG_1_CYL_2_ROLL_AVG | Double
# UASOutput: STG_1_CYL_2_ROC_DEV | Double
# UASOutput: STG_1_CYL_2_ROC_ABS | Double

import pandas as pd
import numpy as np

outputLog = []
from datetime import date,datetime,timedelta,timezone
from as_restapi import restAPI
import as_constants as constants
from as_multi_var_utility import Utility
import pandas as pd
import logging
import numpy as np
import os

def calculate_metrics(df, roc_hours=12, rolling_hours=2):

    # ---------------------------
    # 1. Load data
    # ---------------------------
    # df = pd.read_excel(file_path, engine='openpyxl')

    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    df = df.dropna(subset=['Time'])
    df = df.sort_values('Time').reset_index(drop=True)

    tag_columns = [col for col in df.columns if col != 'Time']

    # ---------------------------
    # 2. Rolling Avg (FIXED)
    # ---------------------------
    df = df.set_index('Time')

    # KEEP SAME COLUMN NAMES
    rolling_df = df[tag_columns].rolling(f'{rolling_hours}h').mean()

    df = df.reset_index()
    rolling_df = rolling_df.reset_index(drop=True)

    # ---------------------------
    # 3. Deviation (FIXED)
    # ---------------------------
    deviation_df = df[tag_columns] - rolling_df
    deviation_pct_df = (deviation_df / rolling_df) * 100

    # NOW rename safely
    rolling_df.columns = [f"{col}_Rolling" for col in tag_columns]
    deviation_df.columns = [f"{col}_Dev" for col in tag_columns]
    deviation_pct_df.columns = [f"{col}_DevPct" for col in tag_columns]

    # ---------------------------
    # 4. ROC (same logic)
    # ---------------------------
    start_time = df.iloc[0]['Time']
    end_time = df.iloc[-1]['Time']

    time_diff = end_time - start_time

    roc_dict = {}

    for col in tag_columns:

        start_value = df.iloc[0][col]
        end_value = df.iloc[-1][col]

        roc_value = np.nan

        if (
            pd.notna(start_value)
            and start_value != 0
            and time_diff >= pd.Timedelta(hours=roc_hours)
        ):
            roc_value = ((end_value - start_value) / start_value) * 100

        roc_dict[f"{col}_ROC"] = roc_value

    roc_df = pd.DataFrame([roc_dict])

    # ---------------------------
    # 5. Final Output (last row)
    # ---------------------------
    final_row = pd.concat(
        [
            df.tail(1).reset_index(drop=True),
            rolling_df.tail(1).reset_index(drop=True),
            deviation_df.tail(1).reset_index(drop=True),
            deviation_pct_df.tail(1).reset_index(drop=True),
            roc_df
        ],
        axis=1
    )

    # ---------------------------
    # 6. Save
    # ---------------------------
    output_file = f"C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/final_output_{roc_hours}hr.xlsx"
    final_row.to_excel(output_file, index=False)

    print("✅ Final Output:")
    print(final_row)
    print("✅ Saved at:", output_file)

    return final_row
 
MAX_DATA_POINTS = 100
TIMEFORMAT = '%m/%d/%Y %H:%M:%S'
assetName = "3RG1702_CC_Unit"  # once asset name is UAS input put (AssetName.Value).strip() here
 
#Set up logging
logger = logging.getLogger(assetName)
logger.setLevel(logging.INFO)
log_file = "\\\\useastexxonweb\\F$\\APMLimits\\" + str(assetName) + "_log.txt"
handler = logging.FileHandler(log_file,mode='w')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('[ %(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Log a test message
logger.info(f'AssetName --------{assetName}')
outputStatus =""
 
#Define file location to save data
filename_API = "\\\\useastexxonweb\\F$\\APMLimits\\" +  assetName + "_API.csv"
filename_Raw = "\\\\useastexxonweb\\F$\\APMLimits\\" +  assetName + "_raw.csv"
 
try:    
    logger.info(f"--- Starting APM Limit Calculation for Asset: {assetName} ---")
    outputStatus += f"Starting Calc\n"
    #Update Attribute and Property names as per asset
    attribute_names = [
        'RunningStatus', 'Speed', 'RB_VIB_X_DE', 'RB_VIB_Y_DE', 'RB_VIB_X_NDE', 'RB_VIB_Y_NDE'
    ]
    attributes = ['.'.join((assetName, attribute_name)) for attribute_name in attribute_names]
    #property_names = ['DCSHighLimit', 'DCSLowLimit', 'MinAllowPctExp']
    #properties = [f"{assetName}.{attribute}.{property}" for attribute in attribute_names for property in property_names]  
   
    interval = 10
    #interval_type ='minutes'
    dataAccess = restAPI(model_store=constants.MODEL_DB_STORE, tsdb_store=constants.TS_DB_STORE)
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=1)
    start_time = datetime.strftime(start_time, constants.TIME_FORMAT_Z)
    end_time = datetime.strftime(end_time, constants.TIME_FORMAT_Z)
    logger.info("Fetching data for last 1 Hour")
    outputStatus += f"Fetching data\n"
 
    #Fetching data from API
    data = pd.DataFrame()
    hasPage = True
    pageNumber = 1
    while hasPage:
        data_payload = {
            "AttributeTrendsRequest": [{
                "AssetName": assetName,
                "AttributeNames": attributes,
                "PropertyNames": []
            }],
            "PageNumber": pageNumber,
            "FromDate": start_time,
            "ToDate": end_time,
            "Options": {
                "OffSetInMinutes": 0,
                "ReturnOnlyGoodData": True,
                "ExcludeNaN": True,
                "MaxPoints": MAX_DATA_POINTS,
                "Aggregate": 3,
                "SamplingIntervalInSec": int(interval*60),
                "IncludeConstantAttribute": True,
                "IsTypeLevelUOM": False
            }
        }
        logger.info("Calling API")
        outputStatus += f"Calling API\n"
        raw_data = dataAccess.import_live_data_v1(data_payload)
        if not raw_data['AttributeTrends']:
            err = f"No data found for this payload {data_payload}"
            logger.info(err)
            outputStatus += f"{err}\n"
            continue
        json_data = [raw_data['AttributeTrends']['AttributeTrends']]
        data_batch = Utility.format_data(json_data, attributes)
        data_batch = data_batch.reset_index()
        data_batch.rename(columns = {'Time': 'Timestamp'}, inplace=True)
        data_batch['Timestamp'] = pd.to_datetime(pd.to_datetime(data_batch['Timestamp']).dt.strftime(TIMEFORMAT))
        data = pd.concat([data, data_batch],ignore_index = True)
        hasPage = raw_data['PageDetail']['HasNextPage']
        if not hasPage:
            break
        pageNumber += 1        
        logger.info("Data fetch completed..Formatting API response into Dataframe")
        outputStatus += f"Data fetch completed\n"


    # ---------------------------
    # 1. Load data
    # ---------------------------

    file_path = "C:/Users/Vipul.Shukla/OneDrive - Shell/Desktop/CCOMS_Deployment_UAS/L2/RawFilesForTesting/RocValueCode/ROC.xlsx"
    df = pd.read_excel(file_path, engine='openpyxl')
    if df["RunningStatus"][0] == 1 and df["RunningStatus"][-1] == 1:
        # ✅ RUN
        result = calculate_metrics(
            file_path,
            roc_hours=12,     # change to 24 for 24hr ROC
            rolling_hours=2   # change if needed
        )
    else:
        msg = "Not Running"

    STG_1_CYL_1_ROLL_AVG.Value = float(result["STG_1_CYL_2_PRD_DISP_Rolling"][0])
    STG_1_CYL_1_ROC_DEV.Value = 
    STG_1_CYL_1_ROC_ABS.Value = 
    STG_1_CYL_2_ROLL_AVG.Value = 
    STG_1_CYL_2_ROC_DEV.Value = 
    STG_1_CYL_2_ROC_ABS.Value = 
    logger.info("--- APM Limit Calculation finished successfully ---")
    OutputStatus.Value = str("Success") + "\n" + str(outputStatus)
    OutputStatus.Quality = QualityBit.Good
except Exception as inst:
    file_name = os.path.basename(__file__) if '__file__' in globals() else 'unknown_file'
    logger.info(f"Failed {inst}")
    OutputStatus.Value = str(outputStatus) + str(inst)
    OutputStatus.Quality = QualityBit.Good