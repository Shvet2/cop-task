# Mail Ballot Data Analysis for Pennsylvania 2020 General Election

This script processes and analyzes the mail ballot request data for the Pennsylvania 2020 General Election. It fetches the data from a public API, processes it to clean and structure it, performs specified analyses, and generates insightful visualizations.

## Features

1. **Data Handling**:
   - Fetches data in batches from an API or loads it from a local file (`downloaded_data.csv`).
   - Cleans the data by removing rows with missing values.
   - Normalizes `senate` district names to snake case.
   - Adds a new column, `yr_born`, derived from `dateofbirth`.

2. **Analysis**:
   - Explores the relationship between voter age and party affiliation.
   - Calculates the median latency for mail ballot processing by legislative district.
   - Identifies the congressional district with the highest number of requests.

3. **Visualization**:
   - Creates a bar chart comparing Democratic and Republican ballot request counts by county.

4. **Outputs**:
   - `processed_data.csv`: Cleaned and structured dataset.
   - `county_party_counts.png`: Visualization of party application counts.

## Requirements

Install the dependencies using the provided `requirements.txt`:

```
$pip install -r requirements.txt
```
## Usage
1.	**Run the Script**:

```
$python3 main.py
```  
2.	**Outputs**:

	•	Processed data saved as processed_data.csv.
	•	Visualization saved as county_party_counts.png.
## Notes

	•	The script uses downloaded_data.csv for subsequent runs after fetching data, speeding up execution.
	•	Ensure all dependencies are installed and the system has internet connectivity for the initial API fetch.
