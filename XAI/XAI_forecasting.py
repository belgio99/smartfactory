import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from aix360.algorithms.lime import LimeTabularExplainer
from typing import Union, Any
import random

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
        - model (Any): A trained forecasting model.
        - training_data (np.ndarray or torch.Tensor): Training data used to fit the LIME explainer.
        - device (torch.device): Device to run the model on (if applicable).
        """
        self.model = model
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))

        # Convert training_data to numpy array if it's a tensor
        if isinstance(training_data, torch.Tensor):
            training_data = training_data.detach().cpu().numpy()
        self.training_data = training_data

        # Prepare data for LIME
        self.num_samples, self.seq_length, self.input_size = self.training_data.shape
        self.training_data_flat = self.training_data.reshape(self.num_samples, self.seq_length * self.input_size)
        self.feature_names = [f'Time_{t}_Feature_{f}' for t in range(self.seq_length) for f in range(self.input_size)]

        # Initialize the LIME explainer
        self.explainer = LimeTabularExplainer(
            self.training_data_flat,
            mode='regression',
            feature_names=self.feature_names,
            verbose=False
        )

    def predict(self, input_data: Union[np.ndarray, torch.Tensor]) -> Any:
        """
        Makes a prediction using the provided model.

        Parameters:
        - input_data (np.ndarray or torch.Tensor): Input data of shape (seq_length, input_size).

        Returns:
        - prediction: The model's prediction.
        """
        # Ensure input_data is a numpy array
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        # Reshape input_data to match model's expected input shape
        if isinstance(self.model, torch.nn.Module):
            # For PyTorch models, keep 3D shape
            input_data_reshaped = input_data.reshape(1, self.seq_length, self.input_size)
            input_tensor = torch.from_numpy(input_data_reshaped).float().to(self.device)
            self.model.eval()
            with torch.no_grad():
                prediction = self.model(input_tensor).cpu().numpy().flatten()
        else:
            # For other models, flatten the input
            input_data_flat = input_data.reshape(1, self.seq_length * self.input_size)
            prediction = self.model.predict(input_data_flat).flatten()

        return prediction

    def predict_with_uncertainty(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        n_samples: int = 100,
        confidence: float = 0.95
    ):
        """
        Makes a prediction with a confidence interval using Monte Carlo Dropout.

        Parameters:
        - input_data (np.ndarray or torch.Tensor): Input data of shape (seq_length, input_size).
        - n_samples (int): Number of forward passes for uncertainty estimation.
        - confidence (float): Confidence level for the interval.

        Returns:
        - mean_pred (float): Mean prediction.
        - lower_bound (float): Lower bound of the confidence interval.
        - upper_bound (float): Upper bound of the confidence interval.
        """
        predictions = []

        # Convert input_data to numpy array if it's a tensor
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        if isinstance(self.model, torch.nn.Module):
            # For PyTorch models, enable dropout during inference
            input_data_reshaped = input_data.reshape(1, self.seq_length, self.input_size)
            input_tensor = torch.from_numpy(input_data_reshaped).float().to(self.device)
            self.model.train()  # Enable dropout layers
            with torch.no_grad():
                for _ in range(n_samples):
                    prediction = self.model(input_tensor).cpu().numpy().flatten()
                    predictions.append(prediction[0])
        else:
            # For other models, uncertainty estimation might not be applicable
            prediction = self.predict(input_data)
            predictions = np.array([prediction[0]] * n_samples)

        predictions = np.array(predictions)
        mean_pred = predictions.mean()
        lower_bound = np.percentile(predictions, ((1 - confidence) / 2) * 100)
        upper_bound = np.percentile(predictions, (confidence + (1 - confidence) / 2) * 100)

        return mean_pred, lower_bound, upper_bound

    def explain_prediction(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        num_features: int = 10,
        verbose: bool = False
    ) -> Any:
        """
        Generates an explanation for the model's prediction on input_data using LIME.

        Parameters:
        - input_data (np.ndarray or torch.Tensor): Input data of shape (seq_length, input_size).
        - num_features (int): Number of features to include in the explanation.
        - verbose (bool): If True, displays the LIME explanation plot.

        Returns:
        - exp: LIME explanation object.
        """
        # Convert input_data to numpy array if it's a tensor
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().cpu().numpy()

        # Flatten input_data
        input_data_flat = input_data.flatten()

        # Define prediction function for LIME
        def predict_fn(data):
            batch_size = data.shape[0]
            if isinstance(self.model, torch.nn.Module):
                # For PyTorch models, reshape to 3D
                inputs = data.reshape(batch_size, self.seq_length, self.input_size)
                inputs_tensor = torch.from_numpy(inputs).float().to(self.device)
                self.model.eval()
                with torch.no_grad():
                    outputs = self.model(inputs_tensor).cpu().numpy()
            else:
                # For other models, reshape to 2D
                inputs = data.reshape(batch_size, self.seq_length * self.input_size)
                outputs = self.model.predict(inputs)
            return outputs.flatten()

        # Generate explanation
        exp = self.explainer.explain_instance(
            input_data_flat,
            predict_fn,
            num_features=num_features
        )

        if verbose:
            self.plot_lime_explanation(exp)

        return exp

    def predict_and_explain(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        n_samples: int = 100,
        confidence: float = 0.95,
        num_features: int = 10,
        verbose: bool = False
    ):
        """
        Combines prediction with uncertainty estimation and explanation.

        Parameters:
        - input_data (np.ndarray or torch.Tensor): Input data of shape (seq_length, input_size).
        - n_samples (int): Number of forward passes for uncertainty estimation.
        - confidence (float): Confidence level for the interval.
        - num_features (int): Number of features to include in the explanation.
        - verbose (bool): If True, displays the LIME explanation plot.

        Returns:
        - mean_pred (float): Mean prediction.
        - lower_bound (float): Lower bound of the confidence interval.
        - upper_bound (float): Upper bound of the confidence interval.
        - exp: LIME explanation object.
        """
        mean_pred, lower_bound, upper_bound = self.predict_with_uncertainty(
            input_data, n_samples=n_samples, confidence=confidence)
        exp = self.explain_prediction(
            input_data, num_features=num_features, verbose=verbose)
        return mean_pred, lower_bound, upper_bound, exp

    @staticmethod
    def plot_lime_explanation(exp, title: str = "LIME Explanation"):
        """
        Plots the LIME explanation.

        Parameters:
        - exp: LIME explanation object.
        - title (str): Title of the plot.
        """
        feature_importance = exp.as_list()
        features, importances = zip(*feature_importance)
        plt.figure(figsize=(10, 6))
        plt.barh(features, importances, color="skyblue")
        plt.title(title)
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.show()

def main():
    # Set random seeds for reproducibility
    np.random.seed(42)
    torch.manual_seed(42)
    random.seed(42)

    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Generate dummy training data
    num_samples = 200
    seq_length = 50
    input_size = 3  # Multidimensional input

    X_train = []
    y_train = []
    for _ in range(num_samples):
        freqs = np.random.uniform(0.1, 0.5, input_size)
        phases = np.random.uniform(0, 2 * np.pi, input_size)
        t = np.linspace(0, 2 * np.pi * seq_length, seq_length)
        x = np.array([np.sin(freq * t + phase) for freq, phase in zip(freqs, phases)]).T
        x += np.random.normal(0, 0.1, x.shape)
        X_train.append(x)
        y_train.append(x[-1, 0])  # Use last value of the first feature as target

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    # Convert data to tensors
    X_train_tensor = torch.from_numpy(X_train).float().to(device)
    y_train_tensor = torch.from_numpy(y_train).float().to(device)

    # Define a more complex PyTorch model with Dropout
    class LSTMForecaster(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, output_size, dropout_rate=0.5):
            super(LSTMForecaster, self).__init__()
            self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout_rate)
            self.dropout = nn.Dropout(dropout_rate)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, x):
            # x: (batch_size, seq_length, input_size)
            out, _ = self.lstm(x)
            out = out[:, -1, :]  # Get output from last time step
            out = self.dropout(out)
            out = self.fc(out)
            return out.squeeze()

    # Initialize the model, loss function, and optimizer
    hidden_size = 64
    num_layers = 2
    output_size = 1
    dropout_rate = 0.3

    model = LSTMForecaster(input_size, hidden_size, num_layers, output_size, dropout_rate).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)

    # Train the model
    num_epochs = 20
    for epoch in range(num_epochs):
        model.train()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 5 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Initialize the forecastExplainer with the model and training data
    explainer = forecastExplainer(model, X_train, device=device)

    # Generate a test instance
    freqs = np.random.uniform(0.1, 0.5, input_size)
    phases = np.random.uniform(0, 2 * np.pi, input_size)
    t = np.linspace(0, 2 * np.pi * seq_length, seq_length)
    x_test = np.array([np.sin(freq * t + phase) for freq, phase in zip(freqs, phases)]).T
    x_test += np.random.normal(0, 0.1, x_test.shape)

    # Use the combined method to get prediction, confidence interval, and explanation
    mean_pred, lower_bound, upper_bound, exp = explainer.predict_and_explain(
        x_test, n_samples=100, confidence=0.95, num_features=10, verbose=True)

    # Print the results
    print(f"Prediction: {mean_pred:.4f}")
    print(f"95% Confidence Interval: [{lower_bound:.4f}, {upper_bound:.4f}]")

    print("\nExplanation:")
    for feature, importance in exp.as_list():
        print(f"{feature}: {importance:.4f}")

if __name__ == '__main__':
    main()

    
    # from statsmodels.tsa.statespace.sarimax import SARIMAX
    model = any
    training_data: Union[np.ndarray, torch.Tensor]
    explainer = forecastExplainer(model, training_data)
    input_data: Union[np.ndarray, torch.Tensor]
    n_predictions: int
    input_labels = ['YYYY-MM-DD', 'YYYY-MM-DD'] 
    Predicted_value, Lower_bound, Upper_bound, Confidence_score, Lime_explaination = explainer.predict_and_explain(input_data, n_predictions, input_labels)
    # Model MUST be able to do prediction = model.predict(input_data)

    '''
    out_dict = {
        'Machine_name': 'MACHINENAME :(',
        'KPI_name': 'KPINAME :)',
        'Predicted_value': [0,1,2,3,4,5,6,7,8,9,10],
        'Lower_bound':[1,1,1,1,1,1,1,1,1,1], #from XAI
        'Upper_bound':[0,0,0,0,0,0,0,0,0,0], #from XAI
        'Confidence_score':[9,8,7,6,5,4,3,2,1,0], #from XAI
        'Lime_explaination': list(('string',2.1),("2",2),("s",1)), #from XAI
        'Measure_unit': 'Kbps',
        'Date_prediction': [d,d,d,d,d,d,d,d,d,d],
        'Forecast': True
    }
    '''