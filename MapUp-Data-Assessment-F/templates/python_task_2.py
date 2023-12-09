import pandas as pd
import datetime

def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    distance_matrix = pd.pivot_table(df, values='distance', index='from_id', columns='to_id', aggfunc='sum', fill_value=0)
    distance_matrix += distance_matrix.T  # Make the matrix symmetric
    distance_matrix.values[[range(len(distance_matrix))]*2] = 0  # Set diagonal values to 0
   

    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here

    unrolled_df = df.melt(id_vars=['from_id'], var_name='to_id', value_name='distance')
    unrolled_df = unrolled_df[unrolled_df['from_id'] != unrolled_df['to_id']].reset_index(drop=True)
    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    # Write your logic here

    reference_avg = df[df['id_start'] == reference_id]['distance'].mean()
    threshold = 0.1 * reference_avg
    selected_ids = df[df['distance'].between(reference_avg - threshold, reference_avg + threshold)]['id_start'].unique()
    return sorted(selected_ids)



def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    for vehicle in rate_coefficients:
        df[vehicle] = df['distance'] * rate_coefficients[vehicle]
    return df

def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here

    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    df['start_day'] = df['start_time'].dt.day_name()
    df['end_day'] = df['end_time'].dt.day_name()

    weekday_discounts = {
        (0, 10): 0.8,
        (10, 18): 1.2,
        (18, 24): 0.8
    }

    weekend_discount = 0.7

    def apply_discount(row):
        if row['start_day'] in ['Saturday', 'Sunday']:
            return weekend_discount
        else:
            for start, end in weekday_discounts:
                if start <= row['start_time'].hour < end:
                    return weekday_discounts[(start, end)]
        return 1.0

    df['discount_factor'] = df.apply(apply_discount, axis=1)
    df['moto'] *= df['discount_factor']
    df['car'] *= df['discount_factor']
    df['rv'] *= df['discount_factor']
    df['bus'] *= df['discount_factor']
    df['truck'] *= df['discount_factor']

    return df.drop(columns='discount_factor')
