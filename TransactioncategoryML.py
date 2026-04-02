import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report

testing_df = pd.read_csv('/srv/dev-disk-by-uuid-9e1c6e06-04c9-4670-9c99-98aaab1929e2/NAS/Scripts/streamlit-config/transactiondata.csv', on_bad_lines='skip')
testing_df.dropna(subset=['Raw SMS'], inplace=True)


# Initialize LabelEncoder for 'Merchant'
le_merchant = LabelEncoder()
testing_df['Merchant_encoded'] = le_merchant.fit_transform(testing_df['Merchant'])
# Initialize LabelEncoder for 'Category'
le_category = LabelEncoder()
testing_df['Category_encoded'] = le_category.fit_transform(testing_df['Category'])

# Define independent and dependent variables
X = testing_df[['Merchant_encoded']]
y = testing_df['Category_encoded']

# Initialize and train the Decision Tree Classifier on the entire dataset
model = DecisionTreeClassifier(random_state=42)
model.fit(X, y)

y_pred = model.predict(X)
# Evaluate the model
accuracy = accuracy_score(y, y_pred)
print(f"\nModel Accuracy (in-sample): {accuracy:.2f}")

def predict_category_using_ML(df):
    # Actual prediction of model
    df['Merchant'] = df['Merchant'].astype(str)

    # --- FIX STARTS HERE ---
    # Store original merchant names before modification
    original_merchants = df['Merchant'].copy()

    # Identify merchants in df that le_merchant has not seen during its fit operation on testing_df
    unseen_merchants_in_df = set(df['Merchant']) - set(le_merchant.classes_)

    if unseen_merchants_in_df:
        print(f"Warning: Found unseen merchants in 'df': {unseen_merchants_in_df}. Mapping them to 'Unknown'.")
        # Replace these unseen merchants in df with 'Unknown'
        df.loc[df['Merchant'].isin(unseen_merchants_in_df), 'Merchant'] = 'Unknown'

    # Now, transform the 'Merchant' column, which should no longer contain unseen labels
    df['Merchant_encoded'] = le_merchant.transform(df['Merchant'])

    predicted_category_encoded = model.predict(df[['Merchant_encoded']])

    predicted_category_decoded = le_category.inverse_transform(predicted_category_encoded)

    df['Category'] = predicted_category_decoded

    # Restore original merchant names after prediction
    df['Merchant'] = original_merchants
    return df
if __name__ == "__main__":
    df = predict_category_using_ML(df)
