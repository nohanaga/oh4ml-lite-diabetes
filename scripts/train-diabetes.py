# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license.

import argparse
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

import matplotlib
matplotlib.use('Agg')

def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", type=str, help="input data")
    parser.add_argument("--model_output", type=str, help="model output", default="./outputs")

    args = parser.parse_args()

    return args

args = parse_args()
lines = [
    f"Training data path: {args.input_data}",
    f"Model output path: {args.model_output}"
]
for line in lines:
    print(line)

with mlflow.start_run():

    diabetes_data = np.loadtxt(args.input_data, delimiter=',',skiprows=1)
    X=diabetes_data[:,0:-1]
    y=diabetes_data[:,-1]
    columns = ['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    data = {
        "train": {"X": X_train, "y": y_train},
        "test": {"X": X_test, "y": y_test}}

    mlflow.log_metric("Training samples", len(data['train']['X']))
    mlflow.log_metric("Test samples", len(data['test']['X']))

    # Log the algorithm parameter alpha to the run
    mlflow.log_metric('alpha', 0.03)
    # Create, fit, and test the scikit-learn Ridge regression model
    regression_model = Ridge(alpha=0.03)
    regression_model.fit(data['train']['X'], data['train']['y'])
    preds = regression_model.predict(data['test']['X'])

    # Log mean squared error
    print('Mean Squared Error is', mean_squared_error(data['test']['y'], preds))
    mlflow.log_metric('mse', mean_squared_error(data['test']['y'], preds))

    # Save the model to the outputs directory for capture
    mlflow.sklearn.save_model(regression_model, args.model_output)

    # Plot actuals vs predictions and save the plot within the run
    fig = plt.figure(1)
    idx = np.argsort(data['test']['y'])
    plt.plot(data['test']['y'][idx], preds[idx])
    fig.savefig("actuals_vs_predictions.png")
    mlflow.log_artifact("actuals_vs_predictions.png")