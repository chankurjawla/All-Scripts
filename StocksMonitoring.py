import pandas as pd
import yfinance as yf
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)      # Helps prevent line wrapping
pd.set_option('display.max_colwidth', None) # Display full content of cells

"""##Price Relative to previous high and low"""

def analyze_stock_prices(tickers):
    """
    Analyzes stock prices for a list of tickers, calculating percentage
    differences from historical highs and lows.

    Args:
        tickers: A list of strings representing stock tickers.

    Returns:
        A pandas DataFrame containing the percentage differences from
        historical highs and lows for each ticker.
    """
    stock_data = {}
    periods_weeks = [52, 26, 13, 8, 4]

    for ticker in tickers:
        ticker_obj = yf.Ticker(ticker)
        hist_data = ticker_obj.history(period="max")

        if hist_data.empty:
            print(f"Could not fetch data for {ticker}. Skipping.")
            continue

        current_price = hist_data['Close'].iloc[-1]
        ticker_high_low = {}

        for period_weeks in periods_weeks:
            period_days = period_weeks * 5
            # Ensure there are enough data points for the period
            if len(hist_data) >= period_days:
                period_hist = hist_data.tail(period_days)
                high = period_hist['High'].max()
                low = period_hist['Low'].min()
                ticker_high_low[f'{period_weeks}_weeks'] = {'high': high, 'low': low}
            else:
                 print(f"Not enough data for {ticker} for {period_weeks} weeks.")
                 ticker_high_low[f'{period_weeks}_weeks'] = {'high': None, 'low': None}

        # Corrected f-strings here to avoid repeated '_weeks'
        stock_data[ticker] = {
            'Current Price': current_price,
            '52_weeks_High': ticker_high_low.get('52_weeks', {}).get('high'),
            '52_weeks_Low': ticker_high_low.get('52_weeks', {}).get('low'),
            '26_weeks_High': ticker_high_low.get('26_weeks', {}).get('high'),
            '26_weeks_Low': ticker_high_low.get('26_weeks', {}).get('low'),
            '13_weeks_High': ticker_high_low.get('13_weeks', {}).get('high'),
            '13_weeks_Low': ticker_high_low.get('13_weeks', {}).get('low'),
            '8_weeks_High': ticker_high_low.get('8_weeks', {}).get('high'),
            '8_weeks_Low': ticker_high_low.get('8_weeks', {}).get('low'),
            '4_weeks_High': ticker_high_low.get('4_weeks', {}).get('high'),
            '4_weeks_Low': ticker_high_low.get('4_weeks', {}).get('low')
        }


    # Convert the stock_data dictionary to a pandas DataFrame
    stock_df = pd.DataFrame.from_dict(stock_data, orient='index')

    # Create a new DataFrame for comparison
    comparison_df = pd.DataFrame(index=stock_df.index)

    # Calculate percentage difference for lows and highs with specified sign conventions
    for period in periods_weeks:
        # Corrected column names to look for
        low_col = f'{period}_weeks_Low'
        high_col = f'{period}_weeks_High'


        # Iterate through each row (ticker) to calculate percentage differences individually
        for index, row in stock_df.iterrows():
            current_price = row['Current Price']
            historical_low = row.get(low_col) # Use .get to avoid KeyError if column doesn't exist
            historical_high = row.get(high_col) # Use .get to avoid KeyError if column doesn't exist

            # Calculate percentage difference from Low
            if historical_low is not None and not pd.isna(historical_low) and historical_low != 0:
                comparison_df.loc[index, f'{period}_weeks_Low_%_Diff'] = ((current_price - historical_low) / historical_low) * 100
            else:
                comparison_df.loc[index, f'{period}_weeks_Low_%_Diff'] = np.nan

            # Calculate percentage difference from High
            if historical_high is not None and not pd.isna(historical_high) and historical_high != 0:
                 comparison_df.loc[index, f'{period}_weeks_High_%_Diff'] = ((historical_high - current_price) / historical_high) * 100 # Corrected formula
            else:
                 comparison_df.loc[index, f'{period}_weeks_High_%_Diff'] = np.nan


    # Reorder columns to have lows on the left and highs on the right
    low_cols = [col for col in comparison_df.columns if 'Low' in col]
    high_cols = [col for col in comparison_df.columns if 'High' in col]
    comparison_df = comparison_df[low_cols + high_cols]

    return comparison_df

"""## Price Consolidation Check"""

def analyze_stock_variability(tickers, duration_buckets_days):
    """
    Analyzes stock price variability for a list of tickers within specified
    duration buckets using the coefficient of variation, with outlier correction.

    Args:
        tickers: A list of strings representing stock tickers.
        duration_buckets_days: A list of integers representing duration buckets in days.

    Returns:
        A pandas DataFrame containing the calculated coefficient of variation for each
        stock and duration bucket after outlier correction.
    """
    variability_data = {}

    for ticker in tickers:
        ticker_obj = yf.Ticker(ticker)
        hist_data = ticker_obj.history(period="2y")

        if hist_data.empty:
            #print(f"Could not fetch data for {ticker}. Skipping.")
            continue

        variability_data[ticker] = {} # Initialize inner dictionary for the ticker

        for duration_days in duration_buckets_days:
            if len(hist_data) >= duration_days:
                closing_prices = hist_data['Close'].tail(duration_days).copy() # Use .copy() to avoid SettingWithCopyWarning

                # --- Outlier Correction (Median +- 3 * Sigma) ---
                median_price = closing_prices.median()
                std_dev = closing_prices.std()

                # Calculate bounds
                lower_bound = median_price - 3 * std_dev
                upper_bound = median_price + 3 * std_dev

                # Replace outliers with bounds
                closing_prices[closing_prices < lower_bound] = lower_bound
                closing_prices[closing_prices > upper_bound] = upper_bound
                # --- End Outlier Correction ---


                mean_price = closing_prices.mean()
                std_dev_corrected = closing_prices.std() # Calculate std dev of corrected prices

                # Calculate coefficient of variation (std_dev / mean)
                if mean_price != 0:
                    coefficient_of_variation = (std_dev_corrected / mean_price) * 100 # Multiply by 100 for percentage
                    variability_data[ticker][f'{duration_days}_days_CoV'] = coefficient_of_variation
                else:
                    variability_data[ticker][f'{duration_days}_days_CoV'] = np.nan # Handle case where mean is zero
            else:
                #print(f"Not enough data for {ticker} for {duration_days} days.")
                variability_data[ticker][f'{duration_days}_days_CoV'] = np.nan


    # Convert the nested dictionary to a pandas DataFrame
    variability_df = pd.DataFrame.from_dict(variability_data, orient='index')

    # Ensure columns are ordered by duration
    ordered_cols = [f'{d}_days_CoV' for d in sorted(duration_buckets_days)]
    # Reindex the DataFrame to enforce the column order, handling potential missing columns
    variability_df = variability_df.reindex(columns=ordered_cols)


    return variability_df

"""## Final Run"""

nifty50_symbols = [
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",
    "BPCL", "BRITANNIA", "CIPLA", "COALINDIA", "DIVISLAB", "DRREDDY",
    "EICHERMOT", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC",
    "JSWSTEEL", "KOTAKBANK", "LT", "LTIM", "M&M", "MARUTI", "NESTLEIND",
    "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SHREECEM",
    "SUNPHARMA", "SWIGGY", "TATACONSUM", "TATASTEEL", "TCS", "TECHM",
    "TITAN", "TRENT", "ULTRACEMCO", "WIPRO","BANKBARODA", "BLUESTARCO",
    "CASTROLIND", "FINCABLES", "FSL", "GESHIP", "IOC", "ITCHOTELS",
    "JIOFIN", "PNB", "POLICYBZR", "PVRINOX",
    "SWIGGY", "TRITURBINE", "YESBANK"
]

# Add .NS suffix to each symbol for yfinance compatibility
nifty50_tickers_list = [symbol + ".NS" for symbol in nifty50_symbols]

tickers_to_analyze = nifty50_tickers_list
stock_comparison_df = analyze_stock_prices(tickers_to_analyze)

# CoV calculation
tickers_list = nifty50_tickers_list
duration_buckets = [30, 60, 90, 180, 250]

variability_results_df = analyze_stock_variability(tickers_list, duration_buckets)

merged_df = pd.concat([stock_comparison_df, variability_results_df], axis=1)
#merged_df = merged_df.sort_index(axis=1)
cov_columns = [col for col in merged_df.columns if '_CoV' in col]
high_columns = [col for col in merged_df.columns if '_High_%_Diff' in col]
low_columns = [col for col in merged_df.columns if '_Low_%_Diff' in col]


# --- Email Configuration ---
SENDER_EMAIL = "raspberrypi574@gmail.com"  # Replace with your email address
SENDER_PASSWORD = "lrji izwh yysf kckm"  # Replace with your email password or App password
RECIPIENT_EMAIL = "ch.ankurjawla@gmail.com" # Replace with the recipient's email address
SMTP_SERVER = "smtp.gmail.com" # e.g., 'smtp.gmail.com' for Gmail
SMTP_PORT = 587 # or 465 for SSL

# --- Prepare the email ---
msg = MIMEMultipart('alternative') # Use 'alternative' to include both plain text and HTML
msg['From'] = SENDER_EMAIL
msg['To'] = RECIPIENT_EMAIL
msg['Subject'] = "Stock Analysis Report: Price Relative to High/Low and Variability"

# Email body - Plain text version
plain_body = "Dear Recipient,\n\nPlease find the stock analysis report below:\n\nThis report includes price relatives to historical highs/lows and variability metrics for the Nifty50 stocks.\n\nBest regards,\nYour Analysis Bot"
msg.attach(MIMEText(plain_body, 'plain'))

# Email body - HTML version with styled DataFrame
# Ensure merged_df, cov_columns, high_columns, low_columns are available in the scope

# Apply the styling to the DataFrame and convert to HTML
styled_df_html = merged_df.style \
    .background_gradient(subset=cov_columns, cmap='RdYlGn_r') \
    .background_gradient(subset=high_columns, cmap='RdYlGn') \
    .background_gradient(subset=low_columns, cmap='RdYlGn_r') \
    .to_html()

html_body = f"""
<html>
  <head></head>
  <body>
    <p>Dear Recipient,</p>
    <p>Please find the stock analysis report below:</p>
    {styled_df_html}
    <p>This report includes price relatives to historical highs/lows and variability metrics for the Nifty50 stocks.</p>
    <p>Best regards,<br>Your Analysis Bot</p>
  </body>
</html>
"""
msg.attach(MIMEText(html_body, 'html'))

# --- Send the email ---
try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls() # Use TLS encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
    print("Please check your email configuration, password, and SMTP server settings.")
    print("For Gmail, ensure 'Less secure app access' is enabled or use an App Password if 2FA is on.")
