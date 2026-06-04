#UASName: APM_Limit_Calculation
#UASDisplayName: APM_Limit_Calculation
#UASDescription: APM_Limit_Calculation
 
# UASInput: RunningStatus | Double
# UASInput: Speed | Double
# UASInput: RB_VIB_X_DE | Double
# UASInput: RB_VIB_Y_DE | Double
# UASInput: RB_VIB_X_NDE | Double
# UASInput: RB_VIB_Y_NDE | Double
# UASInput: RB_VIB_X_DE_DCSHighLimit | Double
# UASInput: RB_VIB_X_NDE_DCSHighLimit | Double
# UASInput: RB_VIB_Y_DE_DCSHighLimit | Double
# UASInput: RB_VIB_Y_NDE_DCSHighLimit | Double
# UASInput: RB_VIB_X_DE_MinAllowPctExp | Double
# UASInput: RB_VIB_X_NDE_MinAllowPctExp | Double
# UASInput: RB_VIB_Y_DE_MinAllowPctExp | Double
# UASInput: RB_VIB_Y_NDE_MinAllowPctExp | Double
 
 
# UASOutput: OutputStatus | String
# UASOutput: RB_VIB_X_DE_HighLimit | Double
# UASOutput: RB_VIB_X_NDE_HighLimit | Double
# UASOutput: RB_VIB_Y_DE_HighLimit | Double
# UASOutput: RB_VIB_Y_NDE_HighLimit | Double
# UASOutput: RB_VIB_X_DE_Expected | Double
 
outputLog = []
from datetime import date,datetime,timedelta,timezone
from as_restapi import restAPI
import as_constants as constants
from as_multi_var_utility import Utility
import pandas as pd
import logging
import numpy as np
import os
 
 
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
 
    #Formatting data  
    data = data.dropna()
    data = data.rename(columns=lambda x: x.replace(str(assetName + '.' + assetName + '.'), ''))
    for col in data.columns:
        if col != 'Timestamp':
            data[col] = pd.to_numeric(data[col], errors='coerce')
    data.sort_values(by='Timestamp', ascending = False)
    #data = data[data['RunningStatus'] >= 0.5] #Add this to filter data based on running status
 
    #saving newly loaded data to csv
    logger.info(f"Saving API fetched data to: {filename_API}")
    outputStatus += f"Saving API data\n"
    data.to_csv(filename_API, index=False, sep=',')
 
    #Reading existing old file.
    logger.info(f"Reading raw data from: {filename_Raw}")
    outputStatus += f"Reading raw data\n"
    data_old= pd.read_csv(filename_Raw)
 
    #Converting Timestamp to datetime format for both files
    data_old['Timestamp'] = pd.to_datetime(pd.to_datetime(data_old['Timestamp']).dt.strftime(TIMEFORMAT))
    data['Timestamp'] = pd.to_datetime(pd.to_datetime(data['Timestamp']).dt.strftime(TIMEFORMAT))
 
    #Combining old and new data, removing data and saving to raw file
    data_combined = pd.concat([data_old, data], ignore_index=True)
    data_combined = data_combined.sort_values(by="Timestamp", ascending=True)
    data_combined = data_combined.drop_duplicates()
    start_time = data_combined['Timestamp'].min()
    cutoff_time = start_time + pd.Timedelta(hours=1)
    #logger.info(f"Removing Data: {data_combined[data_combined['Timestamp'] < cutoff_time]}")
    data_combined = data_combined[data_combined['Timestamp'] >= cutoff_time]    
    data_combined.to_csv(filename_Raw, index=False, sep=',')
    logger.info(f"Final merged data saved to: {filename_Raw}")
    outputStatus += f"Merged data saved\n"
   
    # Get the most recent timestamp from the cleaned data
    normal_data = data_combined
    end_date = normal_data['Timestamp'].max()
    ninety_days_ago = end_date - timedelta(days=90)
    one_eighty_days_ago = end_date - timedelta(days=180)
 
    # Filter data for the last 90 and 180 days
    data_90d = normal_data[normal_data['Timestamp'] >= ninety_days_ago]
    data_180d = normal_data[normal_data['Timestamp'] >= one_eighty_days_ago]
 
    # The list of attributes to process (excluding Timestamp and RunningStatus)
    attributes_to_process = [col for col in normal_data.columns if col not in ['Timestamp', 'RunningStatus']]
   
    # Fetch property values from UAS inputs
    RB_VIB_X_DE_DCSHighLimit = RB_VIB_X_DE_DCSHighLimit.Value
    RB_VIB_X_NDE_DCSHighLimit = RB_VIB_X_NDE_DCSHighLimit.Value
    RB_VIB_Y_DE_DCSHighLimit = RB_VIB_Y_DE_DCSHighLimit.Value
    RB_VIB_Y_NDE_DCSHighLimit = RB_VIB_Y_NDE_DCSHighLimit.Value
    RB_VIB_X_DE_MinAllowPctExp = RB_VIB_X_DE_MinAllowPctExp.Value
    RB_VIB_X_NDE_MinAllowPctExp = RB_VIB_X_NDE_MinAllowPctExp.Value
    RB_VIB_Y_NDE_MinAllowPctExp = RB_VIB_Y_NDE_MinAllowPctExp.Value
    RB_VIB_Y_DE_MinAllowPctExp = RB_VIB_Y_DE_MinAllowPctExp.Value
    logger.info("Fetched property values from UAS inputs")
    outputStatus += f"Fetched property values\n"
 
    for attr in attributes_to_process:
        # Get averages for 90 and 180 day periods
        avg_90d = data_90d[attr].mean()
        avg_180d = data_180d[attr].mean()
       
        logger.info(f"Calculating limits for attribute: {attr}")
        outputStatus += f"\nCalculating limits for {attr}\n"
        logger.info(f"avg_90d = {avg_90d}, avg_180d = {avg_180d}")
 
        # Find the minimum of the available averages
        valid_avgs = [v for v in [avg_90d, avg_180d] if pd.notna(v)]
        if not valid_avgs:
            outputStatus += f"\nWarning: Could not calculate a valid average for {attr}. Skipping limit calculation."
            logger.warning(f"Could not calculate a valid average for {attr}. Skipping limit calculation.")
            continue
        min_avg = min(valid_avgs)
        logger.info(f"Min Reference Avg for {min_avg:.2f}")
        outputStatus += f"\n  - Min Reference Avg (90/180d): {min_avg:.2f}"
 
        dcs_hl = None
        min_allow_pct = None
 
        try:
            # Construct property column names and retrieve the value.
            dcs_hl_col = f"{attr}_DCSHighLimit"
            dcs_hl = locals()[dcs_hl_col]
           
 
            min_allow_pct_col = f"{attr}_MinAllowPctExp"
            min_allow_pct = locals()[min_allow_pct_col]
           
        except IndexError:
            # This occurs if a property column exists but contains no valid data (all NaN).
            outputStatus += f"\nWarning: A property column for {attr} contains no valid data. Skipping."
            logger.warning(f"A property column for {attr} contains no valid data. Skipping.")
            continue
 
        logger.info(f" Fetched Properties DCSHighLimit = {dcs_hl}, MinAllowPctExp = {min_allow_pct}")  
        outputStatus += f"\n  - Fetched Properties: DCSHighLimit={dcs_hl},  MinAllowPctExp={min_allow_pct}"
        #Validate that all required properties were fetched and are valid
        if dcs_hl is None  or min_allow_pct is None:
            outputStatus += f"\nWarning: A required property (DCSHighLimit,  or MinAllowPctExp) not found for {attr}. Skipping."
            logger.warning(f"A required property (DCSHighLimit,  or MinAllowPctExp) not found for {attr}. Skipping.")
            continue
 
        try:
           # Convert the percentage value (e.g., 15) to a decimal factor (e.g., 0.15)
            min_allow_pct = float(min_allow_pct) / 100.0
            outputStatus += f"\n  - min_allow_pct: {min_allow_pct:.2f}"
            logger.info(f"\n  - min_allow_pct: {min_allow_pct:.2f}")
        except (ValueError, TypeError):
            outputStatus += f"\nWarning: Invalid non-numeric MinAllowPctExp value '{min_allow_pct}' for {attr}. Skipping."
            logger.warning(f"Invalid non-numeric MinAllowPctExp value '{min_allow_pct}' for {attr}. Skipping.")
            continue
           
 
       
        # --- High Limit Calculation ---
        hl1 = min_avg + abs(dcs_hl - min_avg) * min_allow_pct
        hl2 = dcs_hl * 0.90
        apm_hl = min(hl1, hl2)
        outputStatus += f"\n  - High Limit Calculation for {attr}: min({hl1:.2f}, {hl2:.2f}) => APM_HL = {apm_hl:.2f}"
        logger.info(f"High Limit Calculation for {attr}: min({hl1:.2f}, {hl2:.2f}) => APM_HL = {apm_hl:.2f}")
 
       
        #Assign calculated limits to output variables
        try:
            apm_hl_name = f"{attr}_HighLimit"
            apm_minavg_name = f"{attr}_Expected"
 
           
            # Assign High Limit
            locals()[apm_hl_name].Value = apm_hl
            locals()[apm_hl_name].Quality = QualityBit.Good
 
            # Assign Min Avg
            locals()[apm_minavg_name].Value = min_avg
            locals()[apm_minavg_name].Quality = QualityBit.Good
                     
        except KeyError as e:
            outputStatus += f"\nError: Output variable '{e.args[0]}' not defined. Cannot assign calculated limit."
            logger.error(f"Output variable '{e.args[0]}' not defined. Cannot assign calculated limit.")
 
    logger.info("--- APM Limit Calculation finished successfully ---")
    OutputStatus.Value = str("Success") + "\n" + str(outputStatus)
    OutputStatus.Quality = QualityBit.Good
except Exception as inst:
    file_name = os.path.basename(__file__) if '__file__' in globals() else 'unknown_file'
    logger.info(f"Failed {inst}")
    OutputStatus.Value = str(outputStatus) + str(inst)
    OutputStatus.Quality = QualityBit.Good