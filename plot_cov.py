import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms

def plot_pose_with_covariance(ax, pose_mean, covariance_matrix, n_std=3.0, **kwargs):
    """
    Plots a 2D pose (mean) and its associated covariance as an ellipse.

    Parameters:
    ax (matplotlib.axes.Axes): The Axes object to draw the ellipse into.
    pose_mean (np.ndarray): A 2-element array representing the (x, y) mean of the pose.
    covariance_matrix (np.ndarray): A 2x2 covariance matrix.
    n_std (float): The number of standard deviations to determine the ellipse's radii.
    **kwargs: Forwarded to matplotlib.patches.Ellipse.
    """
    # Calculate eigenvalues and eigenvectors of the covariance matrix
    eigvals, eigvecs = np.linalg.eigh(covariance_matrix)

    # Calculate the angle of the ellipse (rotation)
    angle = np.degrees(np.arctan2(eigvecs[1, 0], eigvecs[0, 0]))

    # Calculate the width and height of the ellipse
    width, height = 2 * n_std * np.sqrt(eigvals)

    # Create the ellipse patch
    ellipse = Ellipse(xy=pose_mean, width=width, height=height, angle=angle, **kwargs)

    # Add the ellipse to the axes
    ax.add_patch(ellipse)

    # Optionally, plot the mean point
    ax.plot(pose_mean[0], pose_mean[1], 'o', color='red', markersize=5)

# Example Usage:
if __name__ == "__main__":
    # Define a pose mean and covariance matrix
    pose_mean = np.array([1.0, 2.0])
    covariance_matrix = np.array([[0.2, 0.05],
                                  [0.05, 0.1]])

    # Create a figure and axes
    fig, ax = plt.subplots(figsize=(8, 8))

    # Plot the pose with its covariance
    plot_pose_with_covariance(ax, pose_mean, covariance_matrix, n_std=2, facecolor='blue', alpha=0.3)
    plot_pose_with_covariance(ax, pose_mean + 2, covariance_matrix, n_std=2, facecolor='blue', alpha=0.3)

    # Set plot limits and labels
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 4)
    ax.set_xlabel("X-coordinate")
    ax.set_ylabel("Y-coordinate")
    ax.set_title("2D Pose with Covariance Ellipse")
    ax.set_aspect('equal', adjustable='box')
    plt.grid(True)
    plt.show()
    