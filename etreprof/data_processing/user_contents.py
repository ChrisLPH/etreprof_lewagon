import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm

def create_user_topic_enrichment(df_interactions, df_users, df_content_valid):
    """
    Enrich users database with topics
    3 args :
        - df_interactions
        - df_users
        - df_content_valid : the dataframe with the topics
    """
    # Update column types
    df_interactions['created_at'] = pd.to_datetime(df_interactions['created_at'])
    df_interactions['content_id'] = df_interactions['content_id'].astype(str)
    df_content_valid['id'] = df_content_valid['id'].astype(str)

    # We only take the actions of the 3 last years
    cutoff_date = datetime.now() - timedelta(days=365*3)
    df_interactions = df_interactions[df_interactions['created_at'] >= cutoff_date]

    # Join interaction_events + df_content_valid
    df_interactions_filtered = df_interactions.merge(df_content_valid[['id', 'reduced topics']],
            left_on='content_id', right_on='id', how='inner')

    # Drop duplicates of (user_id, content_id) tuple
    df_interactions_unique = df_interactions_filtered.drop_duplicates(subset=['user_id', 'content_id'])

    # Count by topic
    df_user_topic_counts = df_interactions_unique.groupby(['user_id', 'reduced topics']).size().reset_index(name='count')

    # need to pivot the results
    df_topic_matrix = df_user_topic_counts.pivot(
        index='user_id',
        columns='reduced topics',
        values='count'
    ).fillna(0)

    # Add count of different topics and rename
    df_topic_matrix['topic_count'] = (df_topic_matrix > 0).sum(axis=1)
    df_topic_matrix.columns = [f'topic_{col}' if col != 'topic_count'
                           else col for col in df_topic_matrix.columns]

    # Merge with users
    df_users_enriched = df_users.merge(
        df_topic_matrix, left_on='id', right_index=True, how='left'
    ).fillna(0)

    return df_users_enriched

def main_contents_usage(df_contents, df_interactions, df_users, df_content_valid):
    """
    Main function to process user contents usage data from interactions and user CSV files.

    Parameters
    ----------
    df_contents : pandas.DataFrame
        DataFrame containing content data.
    df_interactions : pandas.DataFrame
        DataFrame containing user interactions.
    df_users : pandas.DataFrame
        DataFrame containing user data.
    df_content_valid : pandas.DataFrame
        DataFrame containing valid content data with topics.

    Returns
    -------
    pandas.DataFrame
        DataFrame with enriched user data including content usage statistics.
    """

    df_contents_lite = df_contents[['id', 'type', 'transition_ecologique', 'sante_mentale', 'ecole_inclusive', 'cps',
       'reussite_tous_eleves']]

    df_contents_lite['master_theme'] = None

    df_interactions_filtered = df_interactions[df_interactions.content_type.isin(['contenu', 'guide-pratique', 'fiche-outils'])]

    df_interactions_filtered = df_interactions_filtered[
        ((df_interactions_filtered.content_type == 'contenu') & (df_interactions_filtered.type == "page_view")) |
        ((df_interactions_filtered.content_type == 'guide-pratique') & (df_interactions_filtered.type == "download")) |
        ((df_interactions_filtered.content_type == 'fiche-outils') & (df_interactions_filtered.type == "download"))
    ]

    # CONTENT TYPE FEATURES
    # Count interactions by user and content type
    content_type_features = df_interactions_filtered.groupby(['user_id', 'content_type']).size().unstack(fill_value=0)
    content_type_features.columns = [f'nb_{col.replace("-", "_")}' for col in content_type_features.columns]

    # PRIORITY CHALLENGE FEATURES
    # Merge with df_contents_lite to get priority challenges and themes
    # Fix type mismatch: convert content_id to int to match df_contents_lite id column
    df_interactions_filtered['content_id'] = pd.to_numeric(df_interactions_filtered['content_id'], errors='coerce')

    df_interactions_with_content = df_interactions_filtered.merge(
        df_contents_lite[['id', 'transition_ecologique', 'sante_mentale', 'ecole_inclusive', 'cps', 'reussite_tous_eleves', 'master_theme']],
        left_on='content_id',
        right_on='id',
        how='left'
    )

    # Function to count interactions by priority challenge
    def count_priority_challenge_interactions(df_merged):
        priority_features = pd.DataFrame(index=df_merged['user_id'].unique())
        priority_features.index.name = 'user_id'  # Ensure index has a name

        challenges = ['transition_ecologique', 'sante_mentale', 'ecole_inclusive', 'cps', 'reussite_tous_eleves']

        for challenge in tqdm(challenges, desc="Processing priority challenges"):
            # Filter content that matches this challenge (value = 1)
            challenge_interactions = df_merged[df_merged[challenge] == 1]

            # Count by user_id
            challenge_counts = challenge_interactions.groupby('user_id').size()

            # Add to DataFrame (fill_value=0 for users without interactions on this challenge)
            priority_features[f'nb_{challenge}'] = challenge_counts.reindex(priority_features.index, fill_value=0)

        return priority_features.fillna(0).astype(int)

    priority_features = count_priority_challenge_interactions(df_interactions_with_content)

    # COMBINE INTO FINAL MATRIX
    # Start with unique user_ids
    df_user_features = pd.DataFrame({'user_id': df_interactions_filtered['user_id'].unique()})

    # Merge with content type features
    df_user_features = df_user_features.merge(
        content_type_features.reset_index(),
        on='user_id',
        how='left'
    ).fillna(0)

    # Merge with priority challenge features
    df_user_features = df_user_features.merge(
        priority_features.reset_index(),
        on='user_id',
        how='left'
    ).fillna(0)

    # THEME FEATURES
    # Filter interactions that have a defined master_theme (not None/NaN)
    theme_interactions = df_interactions_with_content.dropna(subset=['master_theme'])

    if not theme_interactions.empty:
        # Count interactions by user and theme
        theme_features = theme_interactions.groupby(['user_id', 'master_theme']).size().unstack(fill_value=0)
        theme_features.columns = [f'nb_theme_{col}' for col in theme_features.columns]

        # Merge with main matrix
        df_user_features = df_user_features.merge(
            theme_features.reset_index(),
            on='user_id',
            how='left'
        ).fillna(0)

    # Total interactions per user
    df_user_features['total_interactions'] = df_interactions_filtered.groupby('user_id').size().values

    # Content diversity (number of unique contents consulted)
    df_user_features['diversite_contenus'] = df_interactions_filtered.groupby('user_id')['content_id'].nunique().values

    # Convert all to integers
    numeric_columns = df_user_features.select_dtypes(include=['float64']).columns
    df_user_features[numeric_columns] = df_user_features[numeric_columns].astype(int)

    # Create DataFrame with user_id uniques
    df_engagement = pd.DataFrame({'user_id': df_interactions['user_id'].unique()})

    # Count each type of interaction by user
    engagement_counts = df_interactions.groupby(['user_id', 'type']).size().unstack(fill_value=0)

    # Add only the columns we are interested in (with 0 if they do not exist)
    df_engagement['nb_vote'] = engagement_counts.get('contenu_vote', 0).values if 'contenu_vote' in engagement_counts.columns else 0
    df_engagement['nb_comments'] = engagement_counts.get('comment_posted', 0).values if 'comment_posted' in engagement_counts.columns else 0
    df_engagement['nb_opened_mail'] = engagement_counts.get('opened_mail', 0).values if 'opened_mail' in engagement_counts.columns else 0
    df_engagement['nb_clicked_mail'] = engagement_counts.get('click_mail', 0).values if 'click_mail' in engagement_counts.columns else 0

    df_users_featured = df_user_features.merge(
                            df_engagement,
                            on='user_id',
                            how='outer'
                        ).fillna(0)

    df_user_final = df_users

    df_users_featured = df_users_featured.rename(columns={'user_id': 'id'})

    df_complete = df_users_featured.merge(
                        df_user_final,
                        on='id',
                        how='right'
                    )

    # Fill with topics enrichment
    df_complete = create_user_topic_enrichment(df_interactions, df_complete, df_content_valid)

    return df_complete
