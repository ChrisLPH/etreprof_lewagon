import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
import time



def create_temporal_engagement_df_optimized(df_interactions):
    """
    Create a temporal user engagement DataFrame from interaction data.

    This function analyzes user interactions to generate engagement metrics across
    different time periods (weeks, months, years) and calculates usage statistics
    for each user.

    Parameters
    ----------
    df_interactions : pandas.DataFrame
        DataFrame containing user interactions with at minimum the columns:
        - 'user_id' : Unique user identifier
        - 'created_at' : Date/time of interaction (will be converted to datetime)

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per unique user containing:

        Identification columns:
        - 'id' : User identifier (formerly user_id)
        - 'join_date' : Date of first interaction
        - 'last_action_date' : Date of last interaction
        - 'total_interactions' : Total number of interactions

        Weekly metrics (12 columns):
        - 'week_minus_0' to 'week_minus_11' : Number of actions per week
          (0 = current week, 11 = 11 weeks ago)

        Monthly metrics (12 columns):
        - 'month_minus_0' to 'month_minus_11' : Number of actions per month
          (0 = current month, 11 = 11 months ago)

        Yearly metrics (3 columns):
        - 'year_minus_0' to 'year_minus_2' : Number of actions per year
          (0 = current year, 2 = 2 years ago)

    Notes
    -----
    - Time periods are calculated retrospectively from datetime.now()
    - Weeks = 7 days, months = 30 days, years = 365 days
    - Rows with missing user_id or created_at are dropped
    - Function displays progress bar via tqdm
    - Execution time is measured and displayed

    Examples
    --------
    >>> df_interactions = pd.DataFrame({
    ...     'user_id': [1, 1, 2, 2, 3],
    ...     'created_at': ['2024-01-01', '2024-01-15', '2024-02-01', '2024-02-10', '2024-03-01']
    ... })
    >>> df_engagement = create_temporal_engagement_df_optimized(df_interactions)
    🚀 Optimized version with groupby + apply...
    📊 Unique users: 3
    📊 Total interactions: 5
    ⚡ Processing...
    ✅ Optimized calculation completed in 0.12 seconds!

    Raises
    ------
    KeyError
        If 'user_id' or 'created_at' columns are missing
    ValueError
        If datetime conversion fails for 'created_at'

    See Also
    --------
    pandas.DataFrame.groupby : Grouping method used for aggregation
    tqdm.pandas : Progress bar for pandas operations
    """

    # Activate tqdm for pandas
    tqdm.pandas()

    start_time = time.time()

    # Prepare
    df_interactions['created_at'] = pd.to_datetime(df_interactions['created_at'])
    df_interactions = df_interactions.dropna(subset=['user_id', 'created_at'])

    print(f"📊 Unique users : {df_interactions['user_id'].nunique()}")
    print(f"📊 Total interactions : {len(df_interactions)}")

    # Define periods
    now = datetime.now()
    weeks = [(now - timedelta(weeks=i+1), now - timedelta(weeks=i)) for i in range(12)]
    months = [(now - timedelta(days=30*(i+1)), now - timedelta(days=30*i)) for i in range(12)]
    years = [(now - timedelta(days=365*(i+1)), now - timedelta(days=365*i)) for i in range(3)]

    def process_user_group(group):
        """
        Process interaction group for a single user to calculate temporal engagement metrics.

        Parameters
        ----------
        group : pandas.DataFrame
            Group of interactions for one user containing 'created_at' column.

        Returns
        -------
        pandas.Series
            Series with engagement metrics: weekly/monthly/yearly counts,
            join_date, last_action_date, and total_interactions.
        """
        dates = group['created_at']

        result = {}

        # Weekks
        for i, (debut, fin) in enumerate(weeks):
            result[f'week_minus_{i}'] = dates[(dates >= debut) & (dates < fin)].count()

        # Months
        for i, (debut, fin) in enumerate(months):
            result[f'month_minus_{i}'] = dates[(dates >= debut) & (dates < fin)].count()

        # Years
        for i, (debut, fin) in enumerate(years):
            result[f'year_minus_{i}'] = dates[(dates >= debut) & (dates < fin)].count()

        # Complementary datas
        result['join_date'] = dates.min()  # First interaction
        result['last_action_date'] = dates.max()  # Last action
        result['total_interactions'] = len(dates)  # Total number of interactions

        return pd.Series(result)

    print("⚡ Run in progress...")
    df_engagement = df_interactions.groupby('user_id').progress_apply(process_user_group).reset_index()

    df_engagement = df_engagement.rename(columns={'user_id': 'id'})

    # Reorder columns
    column_order = ['id', 'join_date', 'last_action_date', 'total_interactions']
    column_order.extend([f'week_minus_{i}' for i in range(12)])
    column_order.extend([f'month_minus_{i}' for i in range(12)])
    column_order.extend([f'year_minus_{i}' for i in range(3)])

    df_engagement = df_engagement[column_order]

    # Total execution time
    end_time = time.time()
    execution_time = end_time - start_time

    print(f"✅ Time elapsed to run processing {execution_time:.2f} secondes!")

    return df_engagement


def main_frequency_users(csv_interactions, csv_users):
    """
    Main function to process user frequency data from interactions and user CSV files.
    """
    # Load the user CSV file into a DataFrame
    df_interactions = pd.read_csv(csv_interactions, low_memory=False)

    # Create the temporal engagement DataFrame
    df_engagement = create_temporal_engagement_df_optimized(df_interactions)

    # Merge the engagement DataFrame with the user DataFrame
    df_users = pd.read_csv(csv_users, low_memory=False)
    df_users_enriched = df_users.merge(df_engagement, on='id', how='left')

    return df_users_enriched
