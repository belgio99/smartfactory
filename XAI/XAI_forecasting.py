import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from aix360.algorithms.lime import LimeTabularExplainer
from typing import Union, Any, List, Tuple
import random
from datetime import datetime, timedelta
import xgboost as xgb

class forecastExplainer:
    def __init__(
        self,
        model: Any,
        training_data: Union[np.ndarray, torch.Tensor],
        device: torch.device = None
    ):
        """
        Initializes the forecastExplainer.
        
        Parameters:
        - model (Any): A trained forecasting model (PyTorch or sklearn-compatible).
        - training_data (np.ndarray or torch.Tensor): Training data of shape (num_samples, seq_length).
        - device (torch.device): Device to run the model on (if applicable).
        """
        self.model = model
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

        # Convert training_data to numpy array if it's a tensor
        if isinstance(training_data, torch.Tensor):
            training_data = training_data.detach().cpu().numpy()
        self.training_data = training_data

        self.num_samples, self.seq_length = self.training_data.shape

        # Compute baseline noise std from training data variability
        data_std = np.std(self.training_data)
        self.bootstrap_noise_std_base = 0.05 * data_std if data_std > 0 else 0.001

    def predict(self, input_data: Union[np.ndarray, torch.Tensor]) -> np.ndarray:
        """
        Makes a single prediction using the provided model.

        Parameters:
        - input_data (np.ndarray or torch.Tensor): Input data of shape (seq_length,).

        Returns:
        - prediction: The model's prediction as a 1D numpy array of shape (1,).
        """
        # Ensure input_data is a numpy array
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        if isinstance(self.model, nn.Module):
            # PyTorch model expects (batch, seq_length, 1)
            input_data_reshaped = input_data.reshape(1, self.seq_length, 1)
            input_tensor = torch.from_numpy(input_data_reshaped).float().to(self.device)
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(input_tensor).cpu().numpy().flatten()
        else:
            # sklearn/xgboost expects (batch, seq_length)
            input_data_reshaped = input_data.reshape(1, -1)
            prediction = self.model.predict(input_data_reshaped).flatten()

        return prediction

    def predict_with_uncertainty(
        self,
        input_data: np.ndarray,
        n_samples: int = 100,
        confidence: float = 0.95,
        step: int = 0
    ) -> Tuple[float, float, float]:
        """
        Makes a prediction with a confidence interval using bootstrapping.
        
        Parameters:
        - input_data (np.ndarray): Input data of shape (seq_length,).
        - n_samples (int): Number of bootstrap samples.
        - confidence (float): Confidence level for the interval.
        - step (int): The step number in the autoregressive forecasting sequence.

        Returns:
        - mean_pred (float)
        - lower_bound (float)
        - upper_bound (float)
        """
        predictions = []
        # Scale noise with step to reflect increasing uncertainty
        bootstrap_noise_std = self.bootstrap_noise_std_base * (1 + step)

        for _ in range(n_samples):
            perturbed_input = input_data + np.random.normal(0, bootstrap_noise_std, size=len(input_data))
            pred = self.predict(perturbed_input)
            predictions.append(pred[0])

        predictions = np.array(predictions)
        mean_pred = predictions.mean()
        lower_bound = np.percentile(predictions, ((1 - confidence) / 2) * 100)
        upper_bound = np.percentile(predictions, (confidence + (1 - confidence) / 2) * 100)

        return mean_pred, lower_bound, upper_bound

    def explain_prediction(
        self,
        input_data: np.ndarray,
        input_labels: List[str],
        num_features: int = 10
    ):
        """
        Generates a LIME explanation for the model's prediction on input_data.
        
        Parameters:
        - input_data (np.ndarray): Input data of shape (seq_length,).
        - input_labels (List[str]): Labels corresponding to each step in input_data.
        - num_features (int): Number of features to include in the explanation.
        
        Returns:
        - explanation: List of (label, importance) pairs for the top features.
        """
        input_data_flat = input_data.flatten()

        def predict_fn(data):
            batch_size = data.shape[0]
            if isinstance(self.model, nn.Module):
                # For PyTorch models, reshape to (batch, seq_length, 1)
                inputs = data.reshape(batch_size, self.seq_length, 1)
                inputs_tensor = torch.from_numpy(inputs).float().to(self.device)
                self.model.eval()
                with torch.no_grad():
                    outputs = self.model(inputs_tensor).cpu().numpy()
            else:
                outputs = self.model.predict(data)
            return outputs.flatten()

        # Create a new LimeTabularExplainer using the current input_labels as feature names
        explainer = LimeTabularExplainer(
            training_data=self.training_data,
            feature_names=input_labels,  # Use the current labels directly
            mode='regression',
            verbose=False
        )

        exp = explainer.explain_instance(
            input_data_flat,
            predict_fn,
            num_features=num_features
        )

        explanation = exp.as_list()
        return explanation

    def predict_and_explain(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        n_predictions: int,
        input_labels: List[str],
        num_features: int = 10,
        confidence: float = 0.95,
        n_samples: int = 100,
        use_mean_pred: bool = False
    ):
        """
        Performs autoregressive prediction and explanation for n_prediction steps.
        
        Parameters:
        - input_data (np.ndarray or torch.Tensor): Initial input sequence of shape (seq_length,).
        - n_predictions (int): Number of autoregressive predictions.
        - input_labels (List[str]): Labels corresponding to the input_data.
        - num_features (int): Number of features for LIME explanation.
        - confidence (float): Confidence level.
        - n_samples (int): Number of bootstrap samples.
        - use_mean_pred (bool): If True, use the mean of bootstrapped predictions as final prediction.
                                If False, use the direct model prediction (raw prediction) as final prediction.
        
        Returns:
        A dictionary with:
        - Predicted_value: List of predicted values
        - Lower_bound: List of lower bounds
        - Upper_bound: List of upper bounds
        - Confidence_score: List of confidence scores
        - Lime_explaination: List of lists of (label, importance)
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        predicted_values = []
        lower_bounds = []
        upper_bounds = []
        confidence_scores = []
        lime_explanations = []

        current_input = input_data.copy()
        current_labels = input_labels.copy()

        for i in range(n_predictions):
            # Compute uncertainties
            mean_pred, lower_bound, upper_bound = self.predict_with_uncertainty(
                current_input, n_samples=n_samples, confidence=confidence, step=i
            )
            # Compute raw prediction
            raw_pred = self.predict(current_input)[0]

            # Choose which value to use as the predicted value
            final_pred = mean_pred if use_mean_pred else raw_pred

            interval_width = upper_bound - lower_bound
            confidence_score = 1.0 / (1e-6 + interval_width)

            explanation = self.explain_prediction(current_input, current_labels, num_features=num_features)

            predicted_values.append(final_pred)
            lower_bounds.append(lower_bound)
            upper_bounds.append(upper_bound)
            confidence_scores.append(confidence_score)
            lime_explanations.append(explanation)

            # Update the input_data for next step
            current_input = np.append(current_input[1:], final_pred)
            # Update the labels (assume daily increments)
            last_label_date = datetime.strptime(current_labels[-1], "%Y-%m-%d")
            new_label_date = last_label_date + timedelta(days=1)
            new_label = new_label_date.strftime("%Y-%m-%d")
            current_labels = current_labels[1:] + [new_label]

        out_dict = {
            'Predicted_value': predicted_values,
            'Lower_bound': lower_bounds,
            'Upper_bound': upper_bounds,
            'Confidence_score': confidence_scores,
            'Lime_explaination': lime_explanations
        }

        return out_dict


def main():
    # Seed
    np.random.seed(42)
    torch.manual_seed(42)
    random.seed(42)

    # Generate a sine wave
    total_points = 300
    seq_length = 50
    t = np.linspace(0, 10*np.pi, total_points)
    data = np.sin(t) + np.random.normal(0, 0.05, size=total_points)

    # Prepare training data for XGBoost: predict next value from last seq_length values
    X_train = []
    y_train = []
    for i in range(total_points - seq_length - 1):
        X_train.append(data[i:i+seq_length])
        y_train.append(data[i+seq_length])

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Train XGBoost model
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3, learning_rate=0.05, random_state=42)
    model.fit(X_train, y_train)

    # Perform predictions beyond the training range
    n_predictions = 20
    input_data = data[(total_points - seq_length - n_predictions): (total_points - n_predictions)]

    # Generate labels for the input_data
    start_date = datetime(2020, 1, 1)
    input_labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(seq_length)]

    # Initialize the explainer
    explainer = forecastExplainer(model, X_train)

    # Perform autoregressive predictions using raw predictions instead of mean of bootstrap:
    results = explainer.predict_and_explain(
        input_data=input_data,
        n_predictions=n_predictions,
        input_labels=input_labels,
        num_features=5,
        confidence=0.95,
        n_samples=100,
        use_mean_pred=False  # Set this to True or False as desired
    )

    print("Results:")
    for key, val in results.items():
        if key == 'Lime_explaination':
            print(f"{key}:")
            for step, expl in enumerate(val):
                print(f"  Step {step+1}: {expl}")
        else:
            print(f"{key}: {val}")


    predicted_values = results['Predicted_value']
    lower_bounds = results['Lower_bound']
    upper_bounds = results['Upper_bound']
    # Suppose predicted_values, lower_bounds, and upper_bounds are lists
    # Each has length n_predictions

    time_indices = np.arange(len(input_data), len(input_data) + n_predictions)

    plt.figure(figsize=(10,6))
    plt.plot(np.arange(len(input_data)), input_data, label='Input Data', marker='o')

    # Plot predicted values
    plt.plot(time_indices, predicted_values, 'r-', label='Predicted value')

    # Plot lower and upper bounds
    plt.plot(time_indices, lower_bounds, 'g--', label='Lower bound')
    plt.plot(time_indices, upper_bounds, 'b--', label='Upper bound')

    plt.title("Forecasting with Confidence Intervals")
    plt.xlabel("Time Steps")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
