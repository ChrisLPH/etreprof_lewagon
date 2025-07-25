import pandas as pd
from user_transforms import main_users_cleaning
from user_frequency import main_frequency_users
from user_contents import main_contents_usage
import os
from dotenv import load_dotenv

# Import databases
# load_dotenv()
# df_users = pd.read_csv(os.getenv("USER_URL_DB"), low_memory=False)
# df_contents = pd.read_csv(os.getenv("CONTENTS_URL_DB"), low_memory=False)
# df_interactions = pd.read_csv(os.getenv("INTERACTIONS_URL_DB"), low_memory=False)

# local paths for testing
df_users = pd.read_csv("raw_data/users.csv", low_memory=False)
df_contents = pd.read_csv("raw_data/contents_v3.csv", low_memory=False)
df_interactions = pd.read_csv("raw_data/interaction_events.csv", low_memory=False)


def main_process_users(df_users, df_contents, df_interactions):
    """
    Main function to process user data, contents, and interactions.

    Parameters
    ----------
    df_users : pandas.DataFrame
        DataFrame containing user data.
    df_contents : pandas.DataFrame
        DataFrame containing content data.
    df_interactions : pandas.DataFrame
        DataFrame containing interaction data.

    Returns
    -------
    pandas.DataFrame
        Processed DataFrame with user features and engagement metrics.
    """

    # Clean user data
    df_users_cleaned = main_users_cleaning(df_users)

    # Process user frequency data
    df_users_enriched = main_frequency_users(df_interactions, df_users_cleaned)

    # Process user contents usage
    df_final = main_contents_usage(df_contents, df_interactions, df_users_enriched)

    return df_final

if __name__ == "__main__":
    df_final = main_process_users(df_users, df_contents, df_interactions)
    df_final.to_csv("data/users_final_dataset.csv", index=False)
