class GPUScorer:
    """
    GPU Qualification Scoring System

    This class implements a weighted scoring system for GPU qualification submissions.
    The final score (0-100) is calculated based on five key metrics with different weights:

    Weights:
    - GPU Utilization (25%): Higher utilization indicates better use of GPU resources
    - Memory Usage (20%): Efficient memory usage is crucial for GPU performance
    - Power Efficiency (25%): Emphasizes energy-efficient computing
    - Completion Time (15%): Speed of processing the benchmark suite
    - Accuracy (15%): Correctness of results

    A perfect score of 100 would require:
    - 100% GPU utilization
    - 100% efficient memory usage
    - 100% power efficiency
    - Completion time of 1 second or less
    - 100% accuracy in calculations
    """
    def __init__(self):
        # Weights for different metrics (total = 1.0)
        self.weights = {
            'gpu_utilization': 0.25,  # Higher utilization is better
            'memory_usage': 0.20,     # Efficient memory usage is better
            'power_efficiency': 0.25,  # Better power efficiency gets higher score
            'completion_time': 0.15,   # Faster completion time is better
            'accuracy': 0.15          # Higher accuracy is better
        }

    def normalize_completion_time(self, time):
        """
        Normalize completion time to a 0-1 scale
        Lower is better, max score at 1 second, min at 300 seconds

        Args:
            time (float): Completion time in seconds

        Returns:
            float: Normalized score between 0 and 1
        """
        return max(0, min(1, (300 - time) / 299))

    def calculate_score(self, metrics):
        """
        Calculate the overall score based on provided metrics

        Args:
            metrics (dict): Dictionary containing the five key metrics:
                          gpu_utilization, memory_usage, power_efficiency,
                          completion_time, and accuracy

        Returns:
            float: Final score from 0-100, rounded to 2 decimal places

        Raises:
            ValueError: If any required metric is missing or invalid
        """
        try:
            score = 0
            # GPU Utilization (higher is better)
            score += metrics['gpu_utilization'] / 100 * self.weights['gpu_utilization']

            # Memory Usage (higher is better when efficient)
            score += metrics['memory_usage'] / 100 * self.weights['memory_usage']

            # Power Efficiency (higher is better)
            score += metrics['power_efficiency'] / 100 * self.weights['power_efficiency']

            # Completion Time (normalized, lower is better)
            score += self.normalize_completion_time(metrics['completion_time']) * self.weights['completion_time']

            # Model Accuracy (higher is better)
            score += metrics['accuracy'] / 100 * self.weights['accuracy']

            # Convert to 0-100 scale and round to 2 decimal places
            return round(score * 100, 2)

        except KeyError as e:
            raise ValueError(f"Missing required metric: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error calculating score: {str(e)}")