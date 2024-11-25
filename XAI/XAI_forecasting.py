import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from aix360.algorithms.lime import LimeTabularExplainer
from typing import Union, Any
import random

# Set random seeds for reproducibility
#np.random.seed(42)
#torch.manual_seed(42)
#random.seed(42)

def explain_model_with_lime(
    model: nn.Module,
    training_data: Union[np.ndarray, torch.Tensor],
    input_data: Union[np.ndarray, torch.Tensor],
    verbose: bool = False
) -> Any:
    """
    Generates an explanation for the model's prediction on input_data using LIME.

    Parameters:
    - model (nn.Module): Trained PyTorch model.
    - training_data (np.ndarray or torch.Tensor): Array or tensor of shape (num_samples, seq_length, input_size).
    - input_data (np.ndarray or torch.Tensor): Array or tensor of shape (seq_length, input_size).
    - verbose (bool, optional): If True, displays the LIME explanation plot. Default is False.

    Returns:
    - exp (Any): LIME explanation object.
    """

    # Convert input_data and training_data to numpy arrays if they are tensors
    if isinstance(input_data, torch.Tensor):
        input_data = input_data.detach().cpu().numpy()
    if isinstance(training_data, torch.Tensor):
        training_data = training_data.detach().cpu().numpy()

    # Flatten the training data to 2D array (num_samples, num_features) for LIME
    # For multidimensional input, flatten both the time steps and the features
    num_samples, seq_length, input_size = training_data.shape
    training_data_flat = training_data.reshape(num_samples, seq_length * input_size)

    # Create feature names for multidimensional inputs
    feature_names = []
    for t in range(seq_length):
        for f in range(input_size):
            feature_names.append(f'Time_{t}_Feature_{f}')

    # Create the LIME explainer with the flattened training data
    explainer = LimeTabularExplainer(
        training_data_flat,
        mode='regression',
        feature_names=feature_names,
        verbose=verbose
    )

    # Define the prediction function for LIME
    def predict_fn(data: np.ndarray) -> np.ndarray:
        """
        Prediction function for LIME explainer.

        Parameters:
        - data (np.ndarray): Array of shape (num_samples, num_features).

        Returns:
        - predictions (np.ndarray): Predicted outputs of shape (num_samples,).
        """
        # Reshape data back to (batch_size, seq_length, input_size)
        batch_size = data.shape[0]
        inputs = data.reshape(batch_size, seq_length, input_size)
        # Convert numpy array to torch tensor
        inputs = torch.from_numpy(inputs).float().to(next(model.parameters()).device)
        # Get model predictions without gradient computation
        with torch.no_grad():
            outputs = model(inputs)
        # Return predictions as numpy array
        return outputs.cpu().numpy().flatten()

    # Flatten the input data to match the shape expected by explainer
    input_data_flat = input_data.flatten()

    # Generate explanation for the input instance
    exp = explainer.explain_instance(
        input_data_flat,
        predict_fn,
        num_features=10
    )

    # Function to visualize LIME explanation
    def plot_lime_explanation(exp, title: str = "LIME Explanation"):
        """
        Plots the LIME explanation.

        Parameters:
        - exp: LIME explanation object.
        - title (str): Title of the plot.
        """
        # Extract feature importance as list of tuples (feature, importance)
        feature_importance = exp.as_list()
        features, importances = zip(*feature_importance)

        # Create horizontal bar plot
        plt.figure(figsize=(10, 6))
        plt.barh(features, importances, color="skyblue")
        plt.title(title)
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.gca().invert_yaxis()  # Invert y-axis to match LIME output order
        plt.grid(True)
        plt.show()

    # If verbose, display the LIME explanation plot
    if verbose:
        plot_lime_explanation(exp)

    # Return the explanation object
    return exp

def main():
    # Device configuration: use GPU if available, else CPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Define a simple RNN model
    class SimpleRNN(nn.Module):
        def __init__(self, input_size: int, hidden_size: int, num_layers: int, output_size: int):
            super(SimpleRNN, self).__init__()
            self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """
            Forward pass of the RNN.

            Parameters:
            - x (torch.Tensor): Input tensor of shape (batch_size, seq_length, input_size).

            Returns:
            - torch.Tensor: Output tensor of shape (batch_size,).
            """
            # x: (batch_size, seq_length, input_size)
            out, _ = self.rnn(x)
            # out: (batch_size, seq_length, hidden_size)
            out = out[:, -1, :]  # Get output from last time step
            # out: (batch_size, hidden_size)
            out = self.fc(out)
            # out: (batch_size, output_size)
            return out.squeeze()

    # Hyperparameters
    input_size = 3  # Changed input_size to 3 for multidimensional input
    hidden_size = 16
    num_layers = 1
    output_size = 1

    # Initialize the model, loss function, and optimizer
    model = SimpleRNN(input_size, hidden_size, num_layers, output_size).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    # Generate dummy training data
    num_samples = 100
    seq_length = 50

    # Generate multidimensional data
    X_train = []
    y_train = []
    for _ in range(num_samples):
        # Generate random frequencies and phases for each feature
        freqs = np.random.uniform(0.1, 0.5, input_size)
        phases = np.random.uniform(0, 2 * np.pi, input_size)
        # Generate time steps
        t = np.linspace(0, 2 * np.pi * seq_length, seq_length)
        # Generate data for each feature
        x = np.array([np.sin(freq * t + phase) for freq, phase in zip(freqs, phases)]).T
        # Add noise
        x += np.random.normal(0, 0.1, x.shape)
        X_train.append(x)
        # Use the last value of the first feature as the target
        y_train.append(x[-1, 0])
    # Convert lists to numpy arrays
    X_train = np.array(X_train)  # Shape: (num_samples, seq_length, input_size)
    y_train = np.array(y_train)

    # Convert to tensors and move to device
    X_train_tensor = torch.from_numpy(X_train).float().to(device)
    y_train_tensor = torch.from_numpy(y_train).float().to(device)

    # Train the model
    num_epochs = 10
    for epoch in range(num_epochs):
        model.train()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 5 == 0:
            print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Generate a test instance
    freqs = np.random.uniform(0.1, 0.5, input_size)
    phases = np.random.uniform(0, 2 * np.pi, input_size)
    t = np.linspace(0, 2 * np.pi * seq_length, seq_length)
    x_test = np.array([np.sin(freq * t + phase) for freq, phase in zip(freqs, phases)]).T
    x_test += np.random.normal(0, 0.1, x_test.shape)
    # x_test shape: (seq_length, input_size)

    # Explain the model prediction on the test instance
    exp = explain_model_with_lime(model, X_train, x_test, verbose=True)

    # Print the explanation
    print("\nExplanation:")
    for feature, importance in exp.as_list():
        print(f"{feature}: {importance:.4f}")

if __name__ == '__main__':
    main()
