import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from aix360.algorithms.lime import LimeTabularExplainer
from typing import Union, Any, List, Tuple
import random
from datetime import datetime, timedelta
import xgboost as xgb
import time

class ForecastExplainer:
    def __init__(
        self,
        model: Any,
        training_data: Union[np.ndarray, torch.Tensor],
        device: torch.device = None
    ):
        """
        Initialize the ForecastExplainer.

        This class handles both PyTorch (nn.Module) and sklearn/xgboost type models.
        It provides methods to:
        - Predict future values given a sequence.
        - Estimate uncertainty via bootstrapping.
        - Explain predictions using LIME.

        Args:
            model (Any): A trained forecasting model (PyTorch nn.Module or sklearn/xgboost model).
            training_data (Union[np.ndarray, torch.Tensor]): Training data of shape (num_samples, seq_length).
            device (torch.device, optional): Device to run the model on (CPU or GPU). If None, it is auto-selected.

        Globals:
            None

        Raises:
            None

        Returns:
            None
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
        Predict a single step ahead given an input sequence.

        Handles both PyTorch and sklearn/xgboost models.

        For PyTorch models:
        - input_data is reshaped to (1, seq_length, 1)
        - A torch.Tensor is created and passed through the model in eval mode without gradients.

        For sklearn/xgboost models:
        - input_data is reshaped to (1, seq_length)
        - The model's 'predict' method is called directly.

        Args:
            input_data (Union[np.ndarray, torch.Tensor]): The input sequence of shape (seq_length,).

        Globals:
            None

        Raises:
            None

        Returns:
            np.ndarray: A 1D numpy array (shape (1,)) representing the model's prediction.
        """
        # Ensure input_data is a numpy array
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        if isinstance(self.model, nn.Module):
            # PyTorch model prediction
            input_data_reshaped = input_data.reshape(1, self.seq_length, 1)
            input_tensor = torch.from_numpy(input_data_reshaped).float().to(self.device)
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(input_tensor).cpu().numpy().flatten()
        else:
            # sklearn/xgboost model prediction
            input_data_reshaped = input_data.reshape(1, -1)
            prediction = self.model.predict(input_data_reshaped).flatten()

        return prediction

    def predict_with_uncertainty(
        self,
        input_data: np.ndarray,
        n_samples: int = 100,
        confidence: float = 0.95,
        step: int = 0
    ) -> Tuple[float, float, float, float]:
        """
        Make a prediction with uncertainty estimation via bootstrapping.

        For PyTorch models:
        - All perturbed samples are passed in a single batch through the model.

        For sklearn/xgboost models:
        - The entire perturbed batch is predicted at once using model.predict.

        Args:
            input_data (np.ndarray): The input sequence of shape (seq_length,).
            n_samples (int, optional): Number of bootstrap samples. Default is 100.
            confidence (float, optional): Confidence level for the interval (e.g. 0.95 for 95%). Default is 0.95.
            step (int, optional): The step number in the autoregressive forecasting sequence. Default is 0.

        Globals:
            None

        Raises:
            None

        Returns:
            Tuple[float, float, float, float]: A tuple containing:
                mean_pred (float): Mean of bootstrap predictions.
                lower_bound (float): Lower bound of the confidence interval.
                upper_bound (float): Upper bound of the confidence interval.
                confidence (float): The confidence level used for the interval.
        """
        # Scale noise with step to reflect increasing uncertainty
        bootstrap_noise_std = self.bootstrap_noise_std_base * (1 + step)

        perturbed_inputs = np.repeat(input_data.reshape(1, -1), n_samples, axis=0) 
        perturbed_inputs += np.random.normal(0, bootstrap_noise_std, size=perturbed_inputs.shape)

        if isinstance(self.model, nn.Module):
            # PyTorch model: run batch through model
            inputs_tensor = torch.from_numpy(perturbed_inputs.reshape(n_samples, self.seq_length, 1)).float().to(self.device)
            self.model.eval()
            with torch.no_grad():
                predictions = self.model(inputs_tensor).cpu().numpy().flatten()
        else:
            # sklearn/xgboost model: predict directly on batch
            predictions = self.model.predict(perturbed_inputs)

        predictions = np.array(predictions)
        mean_pred = predictions.mean()
        lower_bound = np.percentile(predictions, ((1 - confidence) / 2) * 100)
        upper_bound = np.percentile(predictions, (confidence + (1 - confidence) / 2) * 100)

        return mean_pred, lower_bound, upper_bound, confidence

    def explain_prediction(
        self,
        input_data: np.ndarray,
        input_labels: List[str],
        num_features: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Generate a LIME explanation for the model's prediction on input_data.

        A new LimeTabularExplainer is instantiated dynamically with updated feature names
        corresponding to the current input sequence.

        Args:
            input_data (np.ndarray): Input data of shape (seq_length,).
            input_labels (List[str]): Labels corresponding to each step in input_data.
            num_features (int, optional): Number of features to include in the explanation. Default is 10.

        Globals:
            None

        Raises:
            None

        Returns:
            List[Tuple[str, float]]: A list of (feature_label, importance) pairs.
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

        # Instantiate a new LimeTabularExplainer for the current labels
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
    ) -> dict:
        """
        Perform autoregressive prediction and explanation for n_predictions steps.

        Each predicted step updates the input sequence and labels.

        Args:
            input_data (Union[np.ndarray, torch.Tensor]): Initial input sequence of shape (seq_length,).
            n_predictions (int): Number of autoregressive predictions to make.
            input_labels (List[str]): Labels corresponding to the input_data.
            num_features (int, optional): Number of features for LIME explanation. Default is 10.
            confidence (float, optional): Confidence level for interval estimation. Default is 0.95.
            n_samples (int, optional): Number of bootstrap samples for uncertainty estimation. Must be >=100 for meaningful confidence. Default is 100.
            use_mean_pred (bool, optional): If True, use mean of bootstrap predictions as final prediction; else use raw prediction. Default is False.

        Globals:
            None

        Raises:
            None

        Returns:
            dict: A dictionary containing:
                'Predicted_value' (List[float]): List of predicted values.
                'Lower_bound' (List[float]): List of lower bounds.
                'Upper_bound' (List[float]): List of upper bounds.
                'Confidence_score' (List[float]): List of confidence levels used.
                'Lime_explaination' (List[List[Tuple[str,float]]]): LIME explanations per step.
                'Date_prediction' (List[str]): Predicted date labels for each step.
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        predicted_values = []
        lower_bounds = []
        upper_bounds = []
        confidence_scores = []
        lime_explanations = []
        date_predictions = []

        current_input = input_data.copy()
        current_labels = input_labels.copy()

        for i in range(n_predictions):
            # Compute uncertainties
            mean_pred, lower_bound, upper_bound, confidence_level = self.predict_with_uncertainty(
                current_input, n_samples=n_samples, confidence=confidence, step=i
            )
            # Compute raw prediction
            raw_pred = self.predict(current_input)[0]

            # Decide which prediction to use
            final_pred = mean_pred if use_mean_pred else raw_pred

            explanation = self.explain_prediction(current_input, current_labels, num_features=num_features)

            predicted_values.append(final_pred)
            lower_bounds.append(lower_bound)
            upper_bounds.append(upper_bound)
            confidence_scores.append(confidence_level)
            lime_explanations.append(explanation)

            # Update the input_data and labels for the next step
            current_input = np.append(current_input[1:], final_pred)
            last_label_date = datetime.strptime(current_labels[-1], "%Y-%m-%d")
            new_label_date = last_label_date + timedelta(days=1)
            new_label = new_label_date.strftime("%Y-%m-%d")
            current_labels = current_labels[1:] + [new_label]
            date_predictions.append(new_label)

        out_dict = {
            'Predicted_value': predicted_values,
            'Lower_bound': lower_bounds,
            'Upper_bound': upper_bounds,
            'Confidence_score': confidence_scores,
            'Lime_explaination': lime_explanations,
            'Date_prediction': date_predictions
        }

        return out_dict


def main():
    """
    Main entry point to demonstrate the ForecastExplainer class.

    This function:
    - Generates a synthetic sine wave dataset with noise.
    - Trains an XGBoost model for forecasting.
    - Instantiates ForecastExplainer (which internally creates a LimeTabularExplainer).
    - Uses the ForecastExplainer to predict and explain forecast steps.
    - Plots the results.

    Args:
        None

    Globals:
        None

    Raises:
        None

    Returns:
        None
    """
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

    start_time = time.time()
    # Initialize the explainer
    explainer = ForecastExplainer(model, X_train)

    # Perform autoregressive predictions
    results = explainer.predict_and_explain(
        input_data=input_data,
        n_predictions=n_predictions,
        input_labels=input_labels,
        num_features=5,
        confidence=0.95,
        n_samples=100,
        use_mean_pred=False
    )

    end_time = time.time()

    print("Results:")
    for key, val in results.items():
        if key == 'Lime_explaination':
            print(f"{key}:")
            for step, expl in enumerate(val):
                print(f"  Step {step+1}: {expl}")
        else:
            print(f"{key}: {val}")

    # Plot the results as three separate lines
    predicted_values = results['Predicted_value']
    lower_bounds = results['Lower_bound']
    upper_bounds = results['Upper_bound']

    time_indices = np.arange(len(input_data), len(input_data) + n_predictions)

    plt.figure(figsize=(10,6))
    plt.plot(np.arange(len(input_data)), input_data, label='Input Data', marker='o')
    plt.plot(time_indices, predicted_values, 'r-', label='Predicted value')
    plt.plot(time_indices, lower_bounds, 'g--', label='Lower bound')
    plt.plot(time_indices, upper_bounds, 'b--', label='Upper bound')

    plt.title("Forecasting with XGBoost and Empirical Probability in Interval")
    plt.xlabel("Time Steps")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()
    plt.show()

    print(f"Time taken: {end_time - start_time:.2f} seconds")


if __name__ == '__main__':
    main()
