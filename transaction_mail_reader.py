from imapclient import IMAPClient
from email import message_from_bytes
import pandas as pd
import re
from datetime import datetime
import os
from processor import clean_data
from TransactionCategoryML import predict_category_using_ML

HOST = "imap.gmail.com"
USERNAME = "raspberrypi574@gmail.com"
PASSWORD = "lrji izwh yysf kckm"
LABEL = "Transactions"
FILE = "/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS/Scripts/streamlit-config/transactiondata.csv"

def parse_sms(text):
    text = text.strip() # Clean up leading/trailing whitespace

    amount = None
    # Updated regex for amount to handle cases like 'Rs 70.00', 'Rs. 31.00', and 'INR'
    amount_match = re.search(r'(?:Rs|INR)\.?\s*([\d,]+\.?\d*)', text, re.IGNORECASE)
    if amount_match:
        amount = float(amount_match.group(1).replace(",", ""))

    merchant = "Unknown" # Default value

    # Attempt 3: Look for merchant right after 'at' or 'on'
    # Capture words, stopping at numbers or date patterns
    #pattern = r"(?:;|Info|At|on(?!\s*(?:HDFC|ICICI|\d+)))\s+([A-Z0-9\s&.*]+?)(?=\s(?:credited|Available|by|Avl|on|at|\.)|$)"
    #New pattern added and old masked on 02-Apr-2026 
    pattern = r"(?:;|Info|At|from|on(?!\s*(?:HDFC|ICICI|\d+)))\s+([A-Z0-9\s&.*-]+?)(?=\s(?:credited|Available|by|Avl|on|at|\.|UPI)|$)"
    match_at_on = re.search(pattern, text, re.IGNORECASE)
    
    if not match_at_on:
        merchant = "Unknown"
    else:  
        merchant = match_at_on.group(1).strip()
    return {
        "Date": datetime.now().strftime("%m/%d/%Y"),
        "Spender": "Unknown",
        "Paid Through": "Unknown",
        "Amount": amount,
        "Merchant": merchant,
        "Category": "Unknown",
        "Raw SMS": text
    }

with IMAPClient(HOST) as server:
    server.login(USERNAME, PASSWORD)
    print(f"Logged in as {USERNAME}")
    server.select_folder(LABEL)
    messages = server.search(['ALL'])
    print(f"{len(messages)} new transactions found")
    DEST_LABEL = "Processed_Transactions" # The folder you want to move them to
    if not server.folder_exists(DEST_LABEL):
        server.create_folder(DEST_LABEL)
    
    if not messages:
        print("No new transactions")
        exit()

    df = pd.DataFrame(columns=["Date","Spender","Paid Through","Amount","Merchant","Category","Raw SMS"])
    sender_details = []
    extracted_rows = []

    for uid in messages:
        msg = server.fetch([uid], ['BODY[]', 'FLAGS'])[uid]
        raw_email = msg[b'BODY[]']
        message = message_from_bytes(raw_email)

        # Extract the 'From' header
        sender = message.get("From", "Unknown Sender") # Use 'message' instead of 'message_obj'
        
      
        body = ""
        if message.is_multipart():
            for part in message.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                # look for plain text parts, but not attachments
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    body = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')
                    break
        else:
            # not multipart, likely plain text email
            body = message.get_payload(decode=True).decode(message.get_content_charset() or 'utf-8')

        row = parse_sms(body)
        extracted_rows.append(row)
        sender_details.append(sender)
        #df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)

        server.add_flags(uid, [b'\Seen'])
        server.copy(uid, DEST_LABEL)
        server.delete_messages([uid])
    server.expunge()


# After the loop, create the DataFrame all at once
if extracted_rows:
    df = pd.DataFrame(extracted_rows)
    df['Spender'] = sender_details
    
    # Now call your processor
    # df = clean_data(Input_df, Column_name,Querried Column, json_file_name) this process value from "Raw SMS" column
    #df = clean_data(df, "Category", "Merchant", "categories")
    try:
        df_cat = predict_category_using_ML(df) # Added ML code to predict Category of transaction
    except Exception as e:
        print(f'error during ML as : {e}')
        df_cat = clean_data(df, "Category", "Merchant", "categories")
    df_card = clean_data(df_cat, "Paid Through", "Raw SMS", "paidthrough")
  
    final_column_order = ["Date", "Spender","Paid Through","Amount","Merchant", "Category", "Raw SMS"]
    df_final = df_card[final_column_order]
    # Keep only one entry if these three columns match exactly
    df_final = df_final.drop_duplicates(subset=['Raw SMS'], keep='first')
    print(f"New transaction processed : {len(df)}")
    # Save to CSV
    header_needed = not os.path.isfile(FILE)
    df_final.to_csv(FILE, mode='a', index=False, header=header_needed)
