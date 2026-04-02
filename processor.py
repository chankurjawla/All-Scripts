import pandas as pd
import json
import os

def clean_data(df,column,ref_col,json_name):
    df = df
    df.columns = df.columns.str.strip() # Clean column headers

    # 1. Load the categories from the JSON file
    #json_path = os.path.join(os.path.dirname(file_path), 'categories.json')
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'{json_name}.json')
    #with open(json_path, 'r') as f:
    #    category_map = json.load(f)
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Returning uncleaned data.")
        return df
    with open(json_path, 'r') as f:
        category_map = json.load(f)
    def assign_cat(desc):
        desc = str(desc).lower()
        for category, keywords in category_map.items():
            if any(key in desc for key in keywords):
                return category
        return 'Uncategorized'
    
    if ref_col in df.columns:
        #df['Category'] = df['Merchant'].apply(assign_cat)
        df[column] = df[ref_col].apply(assign_cat)
    
    return df
