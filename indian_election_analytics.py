# -*- coding: utf-8 -*-
"""Indian Election Analytics.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S_4w99wKNdPp1AClT_-8Cjj_aAJo4RJV
"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
from scipy.stats import describe
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from scipy.stats import pearsonr

import warnings
warnings.filterwarnings("ignore")

file_path = '/content/GE India 2024.xlsx'  # Replace with the correct path
file_path_02 = '/content/phase_data.xlsx'

phases_load = ['Phase1','Phase2','Phase3','Phase4','Phase5','Phase6','Phase7']
phases = pd.concat(pd.read_excel(file_path_02, sheet_name=phases_load), ignore_index=True)
data = pd.read_excel(file_path, sheet_name='Final Result')
sheets_load = ['Final Result', 'Counted vs polled', 'Victory Margins']

data = pd.concat(pd.read_excel(file_path, sheet_name=sheets_load), ignore_index=True)
data.info()
data.head()

data.columns

print('Data Cleaning and Preprocessing')

data['EVM Votes'] = pd.to_numeric(data['EVM Votes'], errors='coerce')
data['Postal Votes'] = pd.to_numeric(data['Postal Votes'], errors='coerce')
data['Total Votes'] = pd.to_numeric(data['Total Votes'], errors='coerce')
data['% of Votes'] = pd.to_numeric(data['% of Votes'].str.replace('%', ''), errors='coerce')

data['EVM Votes'].fillna(data['EVM Votes'].median(), inplace=True)
data['Postal Votes'].fillna(0, inplace=True)  # Assuming no postal votes if missing
data['Total Votes'].fillna(data['Total Votes'].median(), inplace=True)

data.info()
data.head()

victory_margin = data['Victory Margin']
percentage_of_votes = data['% of Votes']

data.drop(columns=['Victory Margin', '% of Votes'], inplace =True )

print(data.isnull().sum())

print('Exploratory Data Analysis')

numeric_cols = data.select_dtypes(include='number').columns.tolist()
non_numeric_cols = data.select_dtypes(exclude='number').columns.tolist()

print('Numeric Columns: ', numeric_cols)
print('Non-Numeric Columns: ', non_numeric_cols)

numeric_cols = data.select_dtypes(include='number')
numeric_descriptive_stats = numeric_cols.describe()

imputer = SimpleImputer(strategy='mean')
numeric_cols_imputed = pd.DataFrame(imputer.fit_transform(numeric_cols), columns=numeric_cols.columns, index=numeric_cols.index)

detailed_stats = {}
for col in numeric_cols.columns:
    if numeric_cols[col].dtype == 'float64' or numeric_cols[col].dtype == 'int64':
        detailed_stats[col] = describe(numeric_cols[col])

# Here 'nobs' represents the count of non-missing (non-null) values in the dataset.
stats_dict = {
    'count': [result.nobs for result in detailed_stats.values()],
    'mean': [result.mean for result in detailed_stats.values()],
    'std': [result.variance**0.5 for result in detailed_stats.values()],
    'min': [result.minmax[0] for result in detailed_stats.values()],
    '25%': [result.minmax[0] for result in detailed_stats.values()],
    '50%': [result.minmax[0] for result in detailed_stats.values()],
    '75%': [result.minmax[1] for result in detailed_stats.values()],
    'max': [result.minmax[1] for result in detailed_stats.values()],
    'skewness': [result.skewness for result in detailed_stats.values()],
    'curtosis': [result.kurtosis for result in detailed_stats.values()]
}

detailed_stats_data = pd.DataFrame(stats_dict, index=numeric_cols_imputed.columns)
non_numeric_cols = data.select_dtypes(exclude='number')
non_numeric_cols_filled = non_numeric_cols.fillna('Missing')
non_numeric_freq = non_numeric_cols_filled.apply(lambda x: x.value_counts())

print("Numeric Columns Descriptive Statistics: ")
print(numeric_descriptive_stats)
print("\nDetailed Numeric Statistics:")
print(detailed_stats_data)
print("\nNon-Numeric Columns Frequency Counts:")
print(non_numeric_freq)

non_numeric_info = non_numeric_cols.info()
print(non_numeric_info)

non_numeric_cols

for column in non_numeric_cols.columns:
    print(non_numeric_cols[column].value_counts())

candidate_counts = data[data['Candidate'] != 'NOTA']['Candidate'].value_counts()


plt.figure(figsize=(12, 8))
sns.barplot(x=candidate_counts[:20], y=candidate_counts[:20].index, palette='viridis')
plt.title('Top 20 Candidates by Count', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Candidate', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Annotate bar scores
max_count = candidate_counts[:20].max()
for i, count in enumerate(candidate_counts[:20]):
    plt.text(count + max_count * 0.01, i, str(count), va='center', fontsize=12, color='black')

plt.show()

party_counts = data['Party'].value_counts()
plt.figure(figsize=(12, 8))
sns.barplot(x=party_counts[:20], y=party_counts[:20].index, palette='magma')
plt.title('Top 20 Parties by Count', fontsize=16)
plt.xlabel('Count', fontsize=14)
plt.ylabel('Party', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Annotate bar scores
max_count = party_counts[:20].max()
for i, count in enumerate(party_counts[:20]):
    plt.text(count + max_count * 0.01, i, str(count), va='center', fontsize=12, color='black')

plt.show()

print('Voter Turnout Analysis')

total_votes = data['Total Votes']
turnout_mean  = total_votes.mean()
turnout_median  = total_votes.median()
turnout_mode  = total_votes.mode()
turnout_std  = total_votes.std()
turnout_q1 =  total_votes.quantile(0.25)
turnout_q3 =  total_votes.quantile(0.75)
turnout_iqr = turnout_q3 - turnout_q1
turnout_skewness = total_votes.skew()
turnout_kurtosis = total_votes.kurtosis()

print("Voter Turnout Analysis:")
print("- Mean Turnout:", turnout_mean)
print("- Median Turnout:", turnout_median)
print("- Standard Deviation of Turnout:", turnout_std)
print("- 25th Percentile (Q1) Turnout:", turnout_q1)
print("- 75th Percentile (Q3) Turnout:", turnout_q3)
print("- Interquartile Range (IQR) of Turnout:", turnout_iqr)
print("- Skewness of Turnout:", turnout_skewness)
print("- Kurtosis of Turnout:", turnout_kurtosis)

plt.figure(figsize=(12,6))
sns.histplot(total_votes, bins=20, kde=True)
plt.axvline(turnout_mean, color='r', linestyle='--', label=f"Mean: {turnout_mean:.2f}")
plt.axvline(turnout_median, color='g', linestyle='--', label=f'Median: {turnout_median:.2f}')
plt.axvline(turnout_mean + 2*turnout_std, color='y', linestyle='--', label=f'Mean + 2*Std: {turnout_mean + 2*turnout_std:.2f}')
plt.axvline(turnout_mean - 2*turnout_std, color='y', linestyle='--', label=f'Mean - 2*Std: {turnout_mean - 2*turnout_std:.2f}')

plt.title('Distribution of Total Votes With Statistical Measures')
plt.xlabel('Total Votes')
plt.ylabel('Frequency')
plt.legend()
plt.show()

num_samples = len(data)
sample_size = 1000

sample_means = np.zeros(num_samples)

for i in range(num_samples):
    sample = np.random.choice(data['Total Votes'], size=sample_size, replace=True)
    sample_means[i] = np.mean(sample)

plt.figure(figsize=(10,6))
sns.histplot(sample_means, kde=True, color='skyblue')
plt.title('Sampling Distribution of the Mean')
plt.show()

print('Vote Sharing')

data.replace('-', pd.NA, inplace=True)
data['Total Votes'] = pd.to_numeric(data['Total Votes'], errors='coerce')

data = data.dropna(subset=['Total Votes'])
data['Total Constituency Votes'] = data.groupby('Constituency')['Total Votes'].transform('sum')

# vote share as percentage for each candidate
data['Vote Share'] = (data['Total Votes'] / data['Total Constituency Votes']) * 100
party_vote_share = data.groupby('Party')['Vote Share'].sum().reset_index()
party_vote_share['Normalized Vote Share'] = (party_vote_share['Vote Share'] / party_vote_share['Vote Share'].sum()) * 100

top_parties = party_vote_share.sort_values(by='Normalized Vote Share', ascending=False).head(20)

plt.figure(figsize=(14,8))
ax = sns.barplot(data=top_parties, x='Normalized Vote Share', y='Party', palette='viridis')

for i, v in enumerate(top_parties['Normalized Vote Share']):
    ax.text(v + 0.5, i, f"{v:.2f}", color='black', va='center')

plt.title('Top 10 Parties by Vote Share', fontsize=16)
plt.xlabel('Normalized Vote Share (%)', fontsize=14)
plt.ylabel('Party', fontsize=14)

plt.xlim(0, top_parties['Normalized Vote Share'].max() * 1.1)
plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()

data['EVM Z-Score'] = (data['EVM Votes'] - data['EVM Votes'].mean()) / data['EVM Votes'].std()
data['Postal Z-Score'] = (data['Postal Votes'] - data['Postal Votes'].mean()) / data['Postal Votes'].std()

# Flag anomalies with Z-score > 3 or < -3
data['EVM Anomaly'] = np.abs(data['EVM Z-Score']) > 3
data['Postal Anomaly'] = np.abs(data['Postal Z-Score']) > 3

evm_anomalies = data[data['EVM Anomaly']]
postal_anomalies = data[data['Postal Anomaly']]

print("\nEVM Vote Anomalies:\n", evm_anomalies[['Candidate', 'Constituency', 'EVM Votes', 'EVM Z-Score']])
print("\nPostal Vote Anomalies:\n", postal_anomalies[['Candidate', 'Constituency', 'Postal Votes', 'Postal Z-Score']])

print('EVM and Postal Voting Analysis')

data = data[data['Postal Votes'] > 0]
evm_votes_mean = data['EVM Votes'].mean()
postal_votes_mean = data['Postal Votes'].mean()

print("Number of negative or zero EVM Votes:", (data['EVM Votes'] <= 0).sum())
print("Number of negative or zero Postal Votes:", (data['Postal Votes'] <= 0).sum())

data['EVM Votes'].value_counts().sum()

data['Postal Votes'].value_counts().sum()

X = data['S.N'].values.reshape(-1,1)
y_evm = data['EVM Votes'].values.reshape(-1,1)
y_postal = data['Postal Votes'].values.reshape(-1,1)

model_evm = LinearRegression().fit(X, y_evm)
model_postal = LinearRegression().fit(X, y_postal)

y_evm_predict = model_evm.predict(X)
y_postal_predict = model_postal.predict(X)

correlation, _ = pearsonr(data['EVM Votes'], data['Postal Votes'])
print("Correlation Between EVM Votes and Postal Votes:", correlation)


plt.figure(figsize=(12, 6))
plt.scatter(data['S.N'], data['EVM Votes'], label='EVM Votes', color='blue', alpha=0.5)
plt.scatter(data['S.N'], data['Postal Votes'], label='Postal Votes', color='green', alpha=0.5)
plt.plot(data['S.N'], y_evm_predict, color='blue', linestyle='--', label='Trend line (EVM)')
plt.plot(data['S.N'], y_postal_predict, color='green', linestyle='--', label='Trend line (Postal)')
plt.xlabel('Serial Number')
plt.ylabel('Number of Votes')
plt.title('Trend of EVM Votes and Postal Votes')
plt.legend()
plt.grid(True)
plt.show()

print('Victory Margin')

victory_margins = pd.read_excel(file_path, sheet_name='Victory Margins')
merged_data = pd.merge(data, victory_margins, on='Constituency', how='left')

merged_data.info()
merged_data.head()

victory_margins



null_margins = victory_margins.isnull().sum()
# Showing only rows
null_rows = victory_margins.isnull()
null_rows.head()

plt.figure(figsize=(10, 6))
sns.histplot(victory_margins['Victory Margin'], bins=50, kde=True)
plt.title('Distribution of Victory Margins')
plt.xlabel('Margin')
plt.ylabel('Frequency')
plt.show()

top_10_margins = victory_margins.nlargest(10, 'Victory Margin')
bottom_10_margins = victory_margins.nsmallest(10, 'Victory Margin')

print("Top 10 PCs by Victory Margins:\n", top_10_margins[['Constituency', 'Victory Margin']])
print("Bottom 10 PCs by Victory Margins:\n", bottom_10_margins[['Constituency', 'Victory Margin']])

bins_total_votes = pd.cut(data['Total Votes'], bins=10)
bins_victory_margin = pd.cut(victory_margins['Victory Margin'], bins=10)

pivot_table = pd.pivot_table(data, values='Total Votes', index=bins_total_votes, columns=bins_victory_margin, aggfunc='count')

plt.figure(figsize=(12, 8))
sns.heatmap(pivot_table, cmap='YlGnBu', cbar_kws={'label': 'Count of Constituencies'}, annot=False)

x_ticks = [f'{i * 120000}' for i in range(11)]  # Total Votes ranges from 0 to approximately 1,200,000 in steps of 120,000
y_ticks = [f'{i * 50000}' for i in range(11)]   # Victory Margin ranges from 0 to about 500,000 in steps of 50,000
plt.xticks(range(11), x_ticks, rotation=45)
plt.yticks(range(11), y_ticks)

plt.title('Heatmap of Total Votes vs Victory Margin')
plt.xlabel('Total Votes')
plt.ylabel('Victory Margin')
plt.show()

phases.info()

numeric_columns = ['Count of\nElector*', '**Poll (%)', 'Count of\nVotes***', 'Count of Elector*', '**Poll\n(%)', 'Count of Votes***']
data_imputed = phases.copy()

for col in numeric_columns:
    if data_imputed[col].dtype in ['float64', 'int64']:  # Check if the column is numeric
        mean_val = data_imputed[col].mean()
        data_imputed[col].fillna(mean_val, inplace=True)

print(data_imputed.isnull().sum())

data_imputed.dropna(subset=['State', 'PC Name'], how='all', inplace=True)
print(data_imputed.isnull().sum())

data_imputed['Delta Electors'] = data_imputed['Count of\nElector*'].diff()
data_imputed['Delta Votes'] = data_imputed['Count of\nVotes***'].diff()
data_imputed['Delta Phase'] = data_imputed['Sl. No.'].diff()

data_imputed['Average Rate of Change (Electors)'] = data_imputed['Delta Electors'] / data_imputed['Delta Phase']
data_imputed['Average Rate of Change (Votes)'] = data_imputed['Delta Votes'] / data_imputed['Delta Phase']

data_imputed = data_imputed.dropna()

fig, axes = plt.subplots(2,1,figsize=(10,8))
axes[0].plot(data_imputed.index, data_imputed['Average Rate of Change (Electors)'], marker='o', color='blue')
axes[0].set_title('Average Rate of Chage (Electors)')
axes[0].set_xlabel('Phase')
axes[0].set_ylabel('Average Rate of Changes')

axes[1].plot(data_imputed.index, data_imputed['Average Rate of Change (Votes)'], marker='o', color='green')
axes[1].set_title('Average Rate of Change (Votes)')
axes[1].set_xlabel('Phase')
axes[1].set_ylabel('Average Rate of Change')

plt.tight_layout()
plt.show()

numeric_cols = ['Count of\nElector*', '**Poll (%)', 'Count of\nVotes***', 'Count of Elector*', '**Poll\n(%)', 'Count of Votes***']
data_imputed[numeric_cols] = data_imputed[numeric_cols].apply(pd.to_numeric, errors='coerce')


plt.figure(figsize=(12, 6))
sns.lineplot(data=data_imputed, x='Sl. No.', y='Count of\nElector*', label='Count of Electors')
sns.lineplot(data=data_imputed, x='Sl. No.', y='**Poll (%)', label='Poll Percentage')
sns.lineplot(data=data_imputed, x='Sl. No.', y='Count of\nVotes***', label='Count of Votes')
plt.xlabel('Phase')
plt.ylabel('Counts')
plt.title('Trend Analysis Over Phases')
plt.legend()
plt.show()