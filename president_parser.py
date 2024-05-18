import pandas as pd
import os
import json


#Constants
POSITION_BANK = ["president", "chancellor", "provost", "director", "dean", "controller", "trustee", "member", "regent", "chairman", "assistant", "librarian", "secretary", "chaplain", "minister", "treasurer"]


#Put every column from the xlsx into a df
def parse_columns(path):
    df = pd.read_csv(path)
    all_columns = df.iloc[:, :8]
    return all_columns

#Retrieve specific column by index
def retrieve_specific_column(df, index):
    return df.iloc[:, index]


#Return list of members with a specified position (tuple)
#initial test function, wont be used for full process
def extract_presidents(df, value):
    member_list = []
    for index, row in df.iterrows():
        if row.iloc[value] == "President":
            member_list.append(row['Name'])
        elif row.iloc[value] == "Chancellor":
            member_list.append(row['Name'])
    return member_list

#Extract the names of all the institutions for validation
def extract_institutions(df):
    institution_list = []
    for index, row in df.iterrows():
        if row.iloc[2] not in institution_list:
            institution_list.append(row.iloc[2])
    return institution_list


#extract first person from each institution
def extract_first_member(df):
    df['Previous_Value'] = df.iloc[:, 2].shift(1)
    first_member_df = []
    for index, row in df.iterrows():
        current_institution = row.iloc[2]
        previous_institution = row['Previous_Value']
        # Check if the value at index 2 has changed, including handling NaN for the first row
        if pd.isna(previous_institution) or current_institution != previous_institution:
            first_member_df.append(row)
    return pd.DataFrame(first_member_df)

#check if the first person is president and the second is the chancellor (need to decide how to handle these two)

#remove any non presidents/chancellors
def clean_president_list(df):
    cleaned_df = []
    for index, row in df.iterrows():
        if 'president' in row.iloc[1].lower() or 'chancellor' in row.iloc[1].lower() or 'director' in row.iloc[1].lower() or 'superintendent' in row.iloc[1].lower():
            #Don't want vice president of the university, but exceptions
            if 'vice president' not in row.iloc[1].lower():
                cleaned_df.append(row)
            elif row.iloc[1].lower().count('president') >= 2:
                cleaned_df.append(row)
            elif 'vice president' in row.iloc[1].lower() and 'chancellor' in row.iloc[1].lower():
                cleaned_df.append(row)

    cleaned_df = pd.DataFrame(cleaned_df)
    cleaned_df = cleaned_df.map(lambda x: x.title() if isinstance(x, str) else x)

    # cleaned_df = cleaned_df.drop_duplicates(subset = ["Name"], keep = "first")
    cleaned_df = cleaned_df.drop_duplicates(subset = ["Institution"], keep = "first")
    return cleaned_df

#Replace all the entries of a column with a standardized value (for president)
def replace_values(df, string):
    df.iloc[:,1] = string
    return df 

#Find the institutions that were left out from the president list
def find_missing_institutions(institutions, df):
    lowercase_df = df.iloc[:,2].str.lower()
    missing_institutions = []
    for institution in institutions:
        if institution.lower() not in lowercase_df.values:
            missing_institutions.append(institution)
    return missing_institutions

#Provost Functions

#Extract every row with the substring provost in the title
def extract_provost(df):
    provost_df = []
    for index, row in df.iterrows():
        if 'provost' in row.iloc[1].lower():
            provost_df.append(row)
    provost_df = pd.DataFrame(provost_df)
    return provost_df






# -----------  Testing  ----------- #
path_read = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\connectedData\\1999_gptDataframe.csv"
president_path = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\connectedData\\1999_presidents.csv"
provost_path = "C:\\Users\\tykun\\OneDrive\\Documents\\SchoolDocs\\VSCodeProjects\\connectedData\\1999_provost.csv"

full_dataframe = parse_columns(path_read)
all_institutions = extract_institutions(full_dataframe)

#Extracting and cleaning the presidents in the data
presidents_initial = extract_first_member(full_dataframe)
presidents_cleaned = clean_president_list(presidents_initial)
presidents_cleaned = replace_values(presidents_cleaned, "President")
presidents_cleaned.to_csv(president_path, index = False)

#Lists the institutions that were not covered after extracting the presidents
# missing_institutions = find_missing_institutions(all_institutions, presidents_cleaned)
# for x in missing_institutions:
#     print(x)



# provost_initial = extract_provost(full_dataframe)
# provost_cleaned=  extract_first_member(provost_initial)
# provost_cleaned.to_csv(provost_path, index = False)

# missing_institutions = find_missing_institutions(all_institutions, provost_cleaned)
# for x in missing_institutions:
#     print(x)
# print(presidents_cleaned)



