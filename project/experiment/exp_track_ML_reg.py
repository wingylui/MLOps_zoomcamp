from prefect import flow, task
import pandas as pd
import optuna
import mlflow
import mlflow.xgboost
import xgboost as xgb
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from mlflow.tracking import MlflowClient


@task
def read_dataset(path):
    """
    small dataset processing for the ML training
    """
    df = pd.read_csv(path)
    df["Date_Sold"] = pd.to_datetime(df["Date_Sold"])
    df["Year_Sold"] = df["Date_Sold"].dt.year
    df["Month_Sold"] = df["Date_Sold"].dt.month
    df = df.drop(columns= ['Listing_ID','Agency_Name', 'Postcode', 'Date_Sold', 'Address', 'Suburb', 'Longitude', 'Latitude', 'Primary_School_Name',
        'Secondary_School_Name'] )
    
    return df


def catag_feature():
    """
    category features into numeric and category features for data processing in pipeline
    """
    numeric_features = ['Property_Type', 'Bedrooms', 'Bathrooms', 'Parking_Spaces', 'Land_Size', 'Primary_School_Distance', 
                        'Secondary_School_Distance', 'Distance_to_CBD', 'Distance_to_Coast', 'Secondary_ICSEA', 
                        'Primary_ICSEA', 'Year_Sold', 'Month_Sold']

    category_features = []
        
    return category_features, numeric_features
 



def objective(trial):
    # hyperparamter tuning setup

    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1),
        "subsample": trial.suggest_float("subsample", 0.6, 1.0),
        "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
        "objective": "reg:squarederror"
    }

    with mlflow.start_run(nested=True):
        category_features, numeric_features = catag_feature()
        
        numeric_transformer = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="mean")), ("scaler", StandardScaler())
                ]
        )
        # categorical_transformer = Pipeline(
        #     steps=[
        #         ("encoder", OneHotEncoder(handle_unknown="ignore"))
        #     ]
        # )

        preprocessor = ColumnTransformer(
            transformers=[
                ("numerical", numeric_transformer, numeric_features),
                # ("cat", categorical_transformer, category_features),
            ]
        )

        pipeline = Pipeline([
            ("preprocessing", preprocessor),
            ("model", xgb.XGBRegressor(**params))
        ])
        
        # Fit pipeline
        pipeline.fit(X_train_full, y_train_full)

        # loging pipeline
        mlflow.sklearn.log_model(pipeline, "model")

        # Predict and evaluate
        preds = pipeline.predict(X_val)
        rmse = root_mean_squared_error(y_val, preds)

        # Log parameters and metrics
        mlflow.log_params(params)
        mlflow.log_metric("rmse", rmse)

    return rmse
 # ----------------------------------------------



@task (name = "experiemnt_tracking")
def exp_track(df):
    """
    hyperparameter tuning 
    """

    # define Features (X) and target (y)
    X = df.drop(columns=['Price'])  
    y = df['Price']   

    # split training and testing dataset
    X_train_full, X_val, y_train_full, y_val = train_test_split(X, y, test_size=0.25, random_state=100)


    # Enable automatic logging for XGBoost
    mlflow.xgboost.autolog()

    # Start the main MLflow experiment
    mlflow.set_tracking_uri(uri="http://mlflow:5000/")
    mlflow.set_experiment("housing-price-prediction")


    with mlflow.start_run(run_name="optuna_hpo"):
        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=50)

        best_params = study.best_trial.params
        best_rmse = study.best_value

        mlflow.log_params(best_params)
        mlflow.log_metric("best_rmse", best_rmse)

@task
def model_regisry(max_rmse):

    from mlflow.entities import ViewType
    from datetime import datetime


    date = datetime.now().date # today date

    client = MlflowClient(tracking_uri= "http://mlflow:5000/")

    runs = client.search_runs(
        experiment_ids='1',
        filter_string=f"metrics.rmse < {max_rmse}",
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=5,
        order_by=["metrics.rmse ASC"]
    )

    for run in runs:
        rmse_ = run.data.metrics["rmse"]
        print(f"runID: {run.info.run_id}, name: {run.info.run_name}, rmse: {rmse_}")

    # register the first model in the list
    print(f"Fisrt model in the list: {runs[0].info.run_id}")
    run_id = runs[0].info.run_id
    modelURL = f"runs:/{run_id}/model"

    # tags for register model
    tag = {
        "model_type": "xgbRegression",
        "owner": "wing",
        "data_version": "v1.0"
    }

    mlflow.register_model(model_uri=modelURL, 
                          name= "Perth housing price prediction",
                          tags= tag)
    
    registered_models = client.search_registered_models()

    for model in registered_models:
        model_name = model.name
        if model_name == "Perth housing price prediction":
            for v in model.latest_versions:
                model_version = v.version

            # client.transition_model_version_stage(
            #     name= model_name,
            #     version= model_version,
            #     stage="Production",
            # )
            print(f"Perth housing price prediction - {model_version} : moved to production")
        else: 
            pass

    
    return run_id, model_version, model_name

@task
def export_model(model_name, experiement_id):
    client = MlflowClient()
    model_version = client.get_model_version(model_name, experiement_id)

    model_folder_name = model_version.source.replace("models:/", "")

    import shutil

    # moving model folder to depolyment
    source = f"../docker/mlflow-prefect/mlflow/mlartifacts/1/models/{model_folder_name}"
    destination = "../deploy/model"

    shutil.copytree(src=source, dst=destination)



@flow(name = "model_opt_train")
def training_pipeline(path, max_rmse):
    df = read_dataset(path)
    exp_track(df)
    run_id, model_version, model_name = model_regisry(max_rmse)
    export_model(model_name, "1")


if __name__ == "__main__":
    training_pipeline("../dataset/output/completed_dataset.csv", str(30000))