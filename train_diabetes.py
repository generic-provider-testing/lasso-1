import argparse
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import Ridge
import matplotlib.pyplot as plt
import numpy as np

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--alpha', type=float, default=1.0, help='Regularization strength')
parser.add_argument('--run_id', type=str, help='Run ID', required=True)
args = parser.parse_args()

with mlflow.start_run(run_id=args.run_id) as run:
    X, y = load_diabetes(return_X_y=True)
    columns = ['age', 'gender', 'bmi', 'bp', 's1', 's2', 's3', 's4', 's5', 's6']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    data = {
        "train": {"X": X_train, "y": y_train},
        "test": {"X": X_test, "y": y_test}}

    mlflow.log_metric("Training samples", len(data['train']['X']))
    mlflow.log_metric("Test samples", len(data['test']['X']))

    # Log the algorithm parameter alpha to the run
    mlflow.log_param('alpha', args.alpha)
    # Create, fit, and test the scikit-learn Ridge regression model
    regression_model = Ridge(alpha=args.alpha)
    regression_model.fit(data['train']['X'], data['train']['y'])
    preds = regression_model.predict(data['test']['X'])

    # Log mean squared error
    print('Mean Squared Error is', mean_squared_error(data['test']['y'], preds))
    mlflow.log_metric('mse', mean_squared_error(data['test']['y'], preds))

    # Save the model to the outputs directory for capture
    mlflow.sklearn.log_model(regression_model, "model")

    # Plot actuals vs predictions and save the plot within the run
    fig = plt.figure(1)
    idx = np.argsort(data['test']['y'])
    plt.plot(data['test']['y'][idx], preds[idx])
    fig.savefig("actuals_vs_predictions.png")
    mlflow.log_artifact("actuals_vs_predictions.png")