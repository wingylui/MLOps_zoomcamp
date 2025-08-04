import datetime
import time
import logging
import pandas as pd
import pickle
import psycopg2
from pathlib import Path
from prefect import flow, task
from evidently import Dataset
from evidently import DataDefinition
from evidently import Report
from evidently.presets import DataDriftPreset, DataSummaryPreset, RegressionPreset

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# PostgreSQL connection parameters
conn_params = {
    "user": "monitor",
    "password": "password",
    "host": "localhost",
    "port": "5431"
}

# Report presets (combine all in one)
report = Report(metrics=[
    DataDriftPreset(),
    DataSummaryPreset(),
    # RegressionPreset()
], include_tests=True )

# Setup feature mapping
def column_map():
    numeric_features = [
        'Property_Type', 'Bedrooms', 'Bathrooms', 'Parking_Spaces', 'Land_Size',
        'Primary_School_Distance', 'Secondary_School_Distance', 'Distance_to_CBD',
        'Distance_to_Coast', 'Secondary_ICSEA', 'Primary_ICSEA', 'Year_Sold', 'Month_Sold'
    ]
    cat_features = []

    schema = DataDefinition(
    numerical_columns= numeric_features,
    categorical_columns= cat_features,
    )

    # data_definition = DataDefinition(
    #     prediction='prediction',
    #     target='target',
    #     numerical_features=numeric_features,
    #     categorical_features=cat_features
    # )
    
    return numeric_features, cat_features, schema

# Load model
with open("./model/artifacts/model.pkl", "rb") as f:
    dv, model = pickle.load(f)

# Load data
reference_data = pd.read_parquet('../dataset/reference.parquet')
current_data = pd.read_parquet("../dataset/current.parquet")


begin = datetime.datetime(2024, 1, 1, 0, 0)

@task
def prep_db():
    create_table_statement = """
        DROP TABLE IF EXISTS evidently_data_drift;
        CREATE TABLE IF NOT EXISTS evidently_data_drift (
            timestamp TIMESTAMP,
            prediction_drift FLOAT,
            num_drifted_columns INTEGER,
            share_missing_values FLOAT,
            rmse FLOAT,
            mae FLOAT,
            r2_score FLOAT
        );
    """

    with psycopg2.connect(**{**conn_params, "dbname": "postgres"}) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname='test'")
            exists = cur.fetchone()
            if not exists:
                cur.execute("CREATE DATABASE test;")

    # Step 2: Connect to the new 'test' database and create the table
    with psycopg2.connect(**{**conn_params, "dbname": "test"}) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(create_table_statement)


@task
def calculate_metrics(curr, i):
    numeric_features, cat_features, schema= column_map()

    current_data['prediction'] = model.predict(current_data[numeric_features + cat_features].fillna(0))

    reference_dataset = Dataset.from_pandas(
        reference_data[numeric_features + cat_features],
        data_definition=schema
    )

    current_dataset = Dataset.from_pandas(
        current_data[numeric_features + cat_features],
        data_definition=schema
    )

    my_eval = report.run(
        reference_data=reference_dataset,
        current_data=current_dataset,
        # column_mapping=data_definition
    )

    result = my_eval.get_metrics()

    prediction_drift = result['metrics'][0]['result']['dataset_drift']
    num_drifted_columns = result['metrics'][0]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][1]['result']['current']['share_of_missing_values']
    rmse = result['metrics'][2]['result']['rmse']
    mae = result['metrics'][2]['result']['mae']
    r2_score = result['metrics'][2]['result']['r2']

    curr.execute(
        """
        INSERT INTO evidently_data_drift(
            timestamp, prediction_drift, num_drifted_columns,
            share_missing_values, rmse, mae, r2_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (begin + datetime.timedelta(i), prediction_drift, num_drifted_columns,
         share_missing_values, rmse, mae, r2_score)
    )

    
    output_dir = Path("./reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    my_eval.save_html(f"{output_dir}/evidently_report.html") 
    print(f"Evidently report saved to {output_dir}/evidently_report'")


@flow
def batch_monitoring_backfill():
    prep_db()
    SEND_TIMEOUT = 10
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)

    with psycopg2.connect(**{**conn_params, "dbname": "test"}) as conn:
        conn.autocommit = True
        for i in range(0, 27):  # simulate 27 time windows
            with conn.cursor() as curr:
                calculate_metrics(curr, i)

            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send += datetime.timedelta(seconds=10)
            logging.info("Data sent to DB")

if __name__ == '__main__':
    batch_monitoring_backfill()