import yfinance
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64

def create_iqr_colormap(df_pct_change, lower_outlier_bound, upper_outlier_bound, outlier_color='#000000',
                          base_colors=['#FF6666', '#FFFFFF', '#66FF66']):
    """
    Creates a divergent colormap with specific colors for values outside IQR-based bounds.

    Args:
        df_pct_change (pd.DataFrame): DataFrame of percentage changes.
        lower_outlier_bound (float): Lower bound for outliers (Q1 - 1.5 * IQR).
        upper_outlier_bound (float): Upper bound for outliers (Q3 + 1.5 * IQR).
        outlier_color (str): Hex color code for outliers.
        base_colors (list): List of colors for the non-outlier range (e.g., Red, White, Green).

    Returns:
        matplotlib.colors.LinearSegmentedColormap: The custom colormap.
        float: vmin for heatmap.
        float: vmax for heatmap.
    """
    data_min = df_pct_change.min().min()
    data_max = df_pct_change.max().max()

    # Determine vmin and vmax for the colormap. It should cover the entire data range,
    # including potential outliers.
    vmin = min(data_min, lower_outlier_bound)
    vmax = max(data_max, upper_outlier_bound)

    # If the range is very small, adjust to avoid division by zero or issues
    if vmax == vmin:
        vmax = vmin + 1e-6 # Small positive adjustment

    # Normalize the bounds to the [0, 1] range of the colormap
    norm_lower_outlier = (lower_outlier_bound - vmin) / (vmax - vmin)
    norm_upper_outlier = (upper_outlier_bound - vmin) / (vmax - vmin)
    norm_zero_pos = (0 - vmin) / (vmax - vmin) # Position of zero for divergent part

    # Ensure positions are within [0, 1] and in correct order
    norm_lower_outlier = np.clip(norm_lower_outlier, 0, 1)
    norm_upper_outlier = np.clip(norm_upper_outlier, 0, 1)
    norm_zero_pos = np.clip(norm_zero_pos, 0, 1)

    cmap_points = []

    # Outlier color below lower_outlier_bound
    cmap_points.append((0.0, outlier_color))
    cmap_points.append((max(0.0, norm_lower_outlier - 1e-9), outlier_color)) # Transition point

    # Base colors between lower_outlier_bound and upper_outlier_bound
    cmap_points.append((norm_lower_outlier, base_colors[0])) # Start of red
    if norm_zero_pos > norm_lower_outlier and norm_zero_pos < norm_upper_outlier:
        cmap_points.append((norm_zero_pos, base_colors[1])) # White at zero
    cmap_points.append((norm_upper_outlier, base_colors[2])) # End of green

    # Outlier color above upper_outlier_bound
    cmap_points.append((min(1.0, norm_upper_outlier + 1e-9), outlier_color)) # Transition point
    cmap_points.append((1.0, outlier_color))

    # Sort points by position and remove duplicates
    cmap_points = sorted(list(set(cmap_points)), key=lambda x: x[0])

    cmap = LinearSegmentedColormap.from_list("custom_iqr_cmap", cmap_points, N=256)

    return cmap, vmin, vmax

# Modified yfin function
def yfin(time, use_iqr_outliers=False, iqr_factor=1.5, outlier_color='#000000',
         base_colors=['#FF6666', '#FFFFFF', '#66FF66'], save_path=None):
  plt.close('all') # Close all existing figures to prevent extra plots
  if time=='month':
    interval = '1mo'
    start=pd.to_datetime(end)-pd.DateOffset(months=7)
  elif time=='week':
    interval = '1wk'
    start=pd.to_datetime(end)-pd.DateOffset(weeks=5)
  elif time=='day':
    interval = '1d'
    start=pd.to_datetime(end)-pd.DateOffset(days=18)
  else:
      raise ValueError("Invalid 'time' parameter. Choose 'month', 'week', or 'day'.")

  # Download data
  df = yfinance.download(ticker,start= start, end=end,interval=interval)['Close']
  df_pct_change = df.pct_change(fill_method=None).iloc[1:] # Exclude first row with NaNs

  # Prepare colormap
  if use_iqr_outliers:
      # Calculate Q1, Q3, and IQR for the entire DataFrame (stacked to treat all values together)
      Q1 = df_pct_change.stack().quantile(0.25)
      Q3 = df_pct_change.stack().quantile(0.75)
      IQR = Q3 - Q1
      lower_bound_iqr = Q1 - iqr_factor * IQR
      upper_bound_iqr = Q3 + iqr_factor * IQR
      cmap_custom, vmin, vmax = create_iqr_colormap(df_pct_change, lower_bound_iqr, upper_bound_iqr, outlier_color, base_colors=base_colors)
      title_text = f'{time} Percentage Change Heatmap for Indices (IQR Outliers highlighted)'
  else:
      # Default behavior without specific outlier coloring, uses the provided base_colors
      cmap_custom = LinearSegmentedColormap.from_list("pastel_red_white_green",base_colors)
      vmin = None # Let seaborn determine
      vmax = None # Let seaborn determine
      title_text = f'{time} Percentage Change Heatmap for Indices'

  y_labels = df_pct_change.index.strftime('%Y-%m-%d')

  # Create the heatmap on explicitly defined figure and axes
  fig, ax = plt.subplots(figsize=(12, 4))
  sns.heatmap(df_pct_change, annot=True, cmap=cmap_custom, fmt=".1%", linewidths=.8,
              yticklabels=y_labels, vmin=vmin, vmax=vmax, ax=ax) # Pass ax to heatmap

  ax.set_title(title_text) # Set title on the axes
  #ax.set_xlabel('Tickers') # Use ax.set_xlabel if desired
  ax.set_ylabel(f'{time}') # Set ylabel on the axes
  plt.xticks(rotation=45, ha='right')
  plt.yticks(rotation=0)
  fig.tight_layout() # Use fig.tight_layout()

  if save_path:
      fig.savefig(save_path, bbox_inches='tight')
      print(f"Plot saved to: {save_path}")

  plt.show()

  return save_path

# Call the function with IQR outlier coloring enabled and save paths
ticker =['^NSEI','^NSEBANK','^CNXAUTO','^CNXIT','^CNXPHARMA',
         '^CNXFMCG','^CNXMETAL','^CNXREALTY','^CNXENERGY',
         '^CNXMEDIA','^CNXPSUBANK','^CNXFIN',
         'NIFTY_PVT_BANK.NS','NIFTY_OIL_AND_GAS.NS','NIFTY_CONSR_DURBL.NS',
         'NIFTY_HEALTHCARE.NS','^CNXINFRA','NIFTY_INDIA_MFG.NS']
end= pd.to_datetime('today')
month_image_path = yfin('month', use_iqr_outliers=True, outlier_color='black',
                        base_colors=['#FF6666', '#FFFFFF', '#66FF66'], save_path='month_heatmap_iqr.png')
week_image_path = yfin('week', use_iqr_outliers=True, outlier_color='black',
                       base_colors=['#FF6666', '#FFFFFF', '#66FF66'], save_path='week_heatmap_iqr.png')
day_image_path = yfin('day', use_iqr_outliers=True, outlier_color='black',
                      base_colors=['#FF6666', '#FFFFFF', '#66FF66'], save_path='day_heatmap_iqr.png')


# Email configuration
sender_email = 'raspberrypi574@gmail.com'  # <--- REPLACE WITH YOUR EMAIL
sender_password = 'lrji izwh yysf kckm' # <--- REPLACE WITH YOUR EMAIL PASSWORD OR APP PASSWORD
receiver_email = 'ch.ankurjawla@gmail.com' # <--- REPLACE WITH RECIPIENT'S EMAIL
subject = 'Market Indices Heatmap with IQR Outliers'

# Create a multipart message
msg = MIMEMultipart('related')
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# HTML body with CID for the image
html_body = """
<html>
  <body>
    <p>Dear recipient,</p>
    <p>Please find attached the latest market indices heatmap, highlighting IQR-based outliers:</p>
    <img src="cid:myimagemonth"><br>
    <img src="cid:myimageweek"><br>
    <img src="cid:myimageday"><br>
    <p>Best regards,</p>
    <p>Your name</p>
  </body>
</html>
"""

# Attach HTML body
msg.attach(MIMEText(html_body, 'html'))

# Attach images individually
# Month heatmap
with open(month_image_path, 'rb') as fp:
    img_data_month = fp.read()
image_month = MIMEImage(img_data_month, name='month_heatmap_iqr.png')
image_month.add_header('Content-ID', '<myimagemonth>') # Set Content-ID for embedding
msg.attach(image_month)

# Week heatmap
with open(week_image_path, 'rb') as fp:
    img_data_week = fp.read()
image_week = MIMEImage(img_data_week, name='week_heatmap_iqr.png')
image_week.add_header('Content-ID', '<myimageweek>') # Set Content-ID for embedding
msg.attach(image_week)

# Day heatmap
with open(day_image_path, 'rb') as fp:
    img_data_day = fp.read()
image_day = MIMEImage(img_data_day, name='day_heatmap_iqr.png')
image_day.add_header('Content-ID', '<myimageday>') # Set Content-ID for embedding
msg.attach(image_day)

# Connect to SMTP server and send email
try:
    # For Gmail, use 'smtp.gmail.com' and port 587 with TLS
    # For other providers, check their SMTP server details
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls() # Enable TLS encryption
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")
