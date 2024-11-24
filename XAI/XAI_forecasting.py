import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt
from aix360.algorithms.lime import LimeTabularExplainer

def explain_model_with_lime(model, training_data, input_data):
    """
    Generates an explanation for the model's prediction on input_data using LIME.

    Parameters:
    - model: Trained PyTorch model.
    - training_data: Numpy array or tensor of shape (num_samples, seq_length, input_size).
    - input_data: Numpy array or tensor of shape (seq_length, input_size).

    Returns:
    - exp: LIME explanation object.
    """

    # Ensure input_data and training_data are numpy arrays
    if isinstance(input_data, torch.Tensor):
        input_data = input_data.detach().cpu().numpy()
    if isinstance(training_data, torch.Tensor):
        training_data = training_data.detach().cpu().numpy()

    # Flatten the training data for LIME
    training_data_flat = training_data.reshape(training_data.shape[0], -1)

    # Create the LIME explainer
    explainer = LimeTabularExplainer(
        training_data_flat,
        mode='regression',
        feature_names=[f'Time_{i}' for i in range(training_data_flat.shape[1])],
        verbose=True
    )

    # Define the prediction function for LIME
    def predict_fn(data):
        # Reshape data to (batch_size, seq_length, input_size)
        batch_size = data.shape[0]
        seq_length = input_data.shape[0]
        input_size = input_data.shape[1]
        inputs = data.reshape(batch_size, seq_length, input_size)
        inputs = torch.from_numpy(inputs).float().to(next(model.parameters()).device)
        # Get model predictions
        with torch.no_grad():
            outputs = model(inputs)
        return outputs.cpu().numpy().flatten()

    # Flatten the input data
    input_data_flat = input_data.flatten()

    # Generate explanation
    exp = explainer.explain_instance(
        input_data_flat,
        predict_fn,
        num_features=10
    )

    # Visualize LIME explanation
    def plot_lime_explanation(exp, title="LIME Explanation"):
        feature_importance = exp.as_list()
        features, importances = zip(*feature_importance)

        plt.figure(figsize=(10, 6))
        plt.barh(features, importances, color="skyblue")
        plt.title(title)
        plt.xlabel("Importance")
        plt.ylabel("Feature")
        plt.gca().invert_yaxis()  # Invert y-axis to match LIME output order
        plt.grid(True)
        plt.show()

    # Example usage
    plot_lime_explanation(exp)


    return exp

def main():
    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Define a simple RNN model
    class SimpleRNN(nn.Module):
        def __init__(self, input_size, hidden_size, num_layers, output_size):
            super(SimpleRNN, self).__init__()
            self.rnn = nn.RNN(input_size, hidden_size, num_layers, batch_first=True)
            self.fc = nn.Linear(hidden_size, output_size)

        def forward(self, x):
            out, _ = self.rnn(x)
            out = out[:, -1, :]  # Last time step
            out = self.fc(out)
            return out.squeeze()

    # Hyperparameters
    input_size = 1
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
    X_train = []
    y_train = []
    for _ in range(num_samples):
        freq = np.random.uniform(0.1, 0.5)
        phase = np.random.uniform(0, 2 * np.pi)
        noise = np.random.normal(0, 0.1, seq_length)
        x = np.sin(np.linspace(0, 2 * np.pi * freq * seq_length, seq_length) + phase) + noise
        X_train.append(x)
        y_train.append(x[-1])

    X_train = np.array(X_train).reshape(num_samples, seq_length, input_size)
    y_train = np.array(y_train)

    # Convert to tensors
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
            print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}')

    # Generate a test instance
    freq = np.random.uniform(0.1, 0.5)
    phase = np.random.uniform(0, 2 * np.pi)
    noise = np.random.normal(0, 0.1, seq_length)
    x_test = np.sin(np.linspace(0, 2 * np.pi * freq * seq_length, seq_length) + phase) + noise
    x_test = x_test.reshape(seq_length, input_size)

    # Explain the model prediction on the test instance
    exp = explain_model_with_lime(model, X_train, x_test)

    # Print the explanation
    print("\nExplanation:")
    for feature, importance in exp.as_list():
        print(f"{feature}: {importance:.4f}")

if __name__ == '__main__':
    main()
