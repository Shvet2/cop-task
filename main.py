import requests
import pandas as pd
import matplotlib.pyplot as plt
import os

def fetch_data():
    """
    Fetch all data from the Pennsylvania 2020 General Election Mail Ballot Requests dataset.
    
    Data is fetched in batches using the API endpoint. The function handles pagination
    to retrieve all records and returns the data as a pandas DataFrame.

    Returns:
        pd.DataFrame: The complete dataset in a pandas DataFrame.
    """
    count_url = "https://data.pa.gov/resource/mcba-yywm.json?$select=count(*)"
    response = requests.get(count_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch total count with status {response.status_code}")
    
    total_count = int(response.json()[0]['count'])
    print(f"Total rows in dataset: {total_count}")

    API_ENDPOINT = "https://data.pa.gov/resource/mcba-yywm.json"
    limit = 50000
    offset = 0
    all_data = []

    print("Starting data fetch from API...")

    while offset < total_count:
        print(f"Fetching records with offset {offset}...")
        params = {'$limit': limit, '$offset': offset}
        response = requests.get(API_ENDPOINT, params=params, timeout=60)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code}. Exiting.")
            break

        data_batch = response.json()
        batch_count = len(data_batch)
        print(f"Received {batch_count} records.")

        if batch_count == 0:
            print("No more data available. Stopping fetch.")
            break

        all_data.extend(data_batch)
        offset += limit

    print("Data fetch complete.")
    return pd.DataFrame(all_data)

def main():
    """
    Main function to process Pennsylvania 2020 General Election Mail Ballot Requests dataset.
    
    Steps:
    1. Fetch or load data from a local CSV.
    2. Remove rows with null values and separate invalid data.
    3. Convert senate district entries to snake_case.
    4. Create a 'yr_born' column based on 'dateofbirth'.
    5. Analyze age-party relationships and calculate median latency for ballot returns.
    6. Identify the top congressional district by ballot requests.
    7. Create a visualization for Republican vs Democratic application counts by county.
    8. Save processed data to a CSV.
    """
    # Load data from local CSV if available, else fetch from API
    if os.path.exists("downloaded_data.csv"):
        print("Reading data from downloaded_data.csv")
        application_in = pd.read_csv("downloaded_data.csv")
    else:
        application_in = fetch_data()
        print("Data fetched. Number of rows:", len(application_in))
        application_in.to_csv("downloaded_data.csv", index=False)
        print("Data saved locally as downloaded_data.csv.")

    if application_in.empty:
        print("No data available. Exiting.")
        return

    print("Columns in application_in:", application_in.columns.tolist())

    # Separate invalid data (rows with nulls)
    invalid_data = application_in[application_in.isnull().any(axis=1)].copy()
    print(f"Invalid data count (rows with nulls): {len(invalid_data)}")

    # Drop rows with null values
    application_in = application_in.dropna()
    print(f"Valid data count after dropping nulls: {len(application_in)}")

    # Convert senate column to snake_case
    if 'senate' in application_in.columns:
        application_in['senate'] = application_in['senate'].str.replace(" ", "_").str.lower()
        print("Converted 'senate' column to snake_case.")
    else:
        print("'senate' column not found, skipping conversion.")

    # Create yr_born column
    if 'dateofbirth' in application_in.columns:
        application_in['yr_born'] = pd.to_datetime(application_in['dateofbirth'], errors='coerce').dt.year
        cols = application_in.columns.tolist()
        dob_index = cols.index('dateofbirth')
        cols.insert(dob_index + 1, cols.pop(-1))  # Move 'yr_born' to the correct position
        application_in = application_in[cols]
        print("'yr_born' column created and placed after 'dateofbirth'.")
    else:
        print("'dateofbirth' column not found, skipping 'yr_born' creation.")

    # Analyze age-party relationship
    if {'party', 'yr_born'}.issubset(application_in.columns):
        application_in['age'] = 2020 - application_in['yr_born']
        age_party_counts = application_in.groupby(['party', 'age']).size().reset_index(name='request_count')
        print("Age-Party distribution sample:")
        print(age_party_counts.head())
    else:
        print("Cannot analyze age-party relationship due to missing columns.")

    # Median latency by legislative district
    if {'appissuedate', 'ballotreturneddate', 'legislative'}.issubset(application_in.columns):
        application_in['appissuedate'] = pd.to_datetime(application_in['appissuedate'], errors='coerce')
        application_in['ballotreturneddate'] = pd.to_datetime(application_in['ballotreturneddate'], errors='coerce')
        application_in = application_in.dropna(subset=['appissuedate', 'ballotreturneddate'])
        application_in['latency_days'] = (application_in['ballotreturneddate'] - application_in['appissuedate']).dt.days
        median_latency = application_in.groupby('legislative')['latency_days'].median().reset_index(name='median_latency_days')
        print("Median latency by legislative district sample:")
        print(median_latency.head())
    else:
        print("Cannot compute median latency. Required columns are missing.")

    # Top congressional district by ballot requests
    if 'congressional' in application_in.columns:
        congressional_counts = application_in.groupby('congressional').size().reset_index(name='request_count')
        top_congressional = congressional_counts.sort_values('request_count', ascending=False).head(1)
        print("Top congressional district by ballot requests:")
        print(top_congressional)
    else:
        print("'congressional' column not found, skipping.")

    # Visualization for Democratic vs Republican applications
    party_mapping = {
        'D': 'DEM',
        'R': 'REP',
        'NOP': 'Other',
        '3RD': 'Other',
        'AC': 'Other'
    }
    application_in['party'] = application_in['party'].map(party_mapping).fillna('Other')
    if {'countyname', 'party'}.issubset(application_in.columns):
        county_party_counts = application_in.groupby(['countyname', 'party']).size().unstack(fill_value=0)
        if {'DEM', 'REP'}.issubset(county_party_counts.columns):
            subset = county_party_counts[['DEM', 'REP']].copy().sort_values('DEM', ascending=False).head(20)
            subset.plot(kind='bar', figsize=(12, 8))
            plt.title("Democratic vs Republican Application Counts by County")
            plt.xlabel("County")
            plt.ylabel("Number of Applications")
            plt.tight_layout()
            plt.savefig("county_party_counts.png")
            print("Visualization saved as county_party_counts.png.")
        else:
            print("DEM and/or REP columns not found in party distribution.")
    else:
        print("'countyname' or 'party' column missing. Cannot create visualization.")

    # Save processed data
    application_in.to_csv("processed_data.csv", index=False)
    print("Processed data saved as processed_data.csv.")
    print("Script execution completed.")

if __name__ == "__main__":
    main()