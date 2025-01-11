from jsonschema import validate, ValidationError

submission_schema = {
    "type": "object",
    "description": """
    GPU Qualification Submission Schema

    This schema defines the structure for GPU qualification submissions. Each submission
    must include the following metrics to evaluate GPU performance:

    - gpu_utilization: Percentage of GPU compute units utilized during the benchmark
    - memory_usage: Percentage of GPU memory efficiently used during processing
    - power_efficiency: Ratio of performance achieved per watt of power consumed
    - completion_time: Time taken to complete the standard benchmark suite (in seconds)
    - accuracy: Percentage of correct results in the benchmark calculations
    """,
    "properties": {
        "gpu_utilization": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Percentage of GPU compute units effectively utilized (0-100%)"
        },
        "memory_usage": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Percentage of GPU memory efficiently used (0-100%)"
        },
        "power_efficiency": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Power efficiency score based on performance per watt (0-100%)"
        },
        "completion_time": {
            "type": "number",
            "minimum": 0,
            "description": "Time to complete benchmark suite in seconds (lower is better)"
        },
        "accuracy": {
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "description": "Percentage of correct results in benchmark calculations (0-100%)"
        }
    },
    "required": ["gpu_utilization", "memory_usage", "power_efficiency", 
                "completion_time", "accuracy"],
    "additionalProperties": False
}

def validate_submission(data):
    """
    Validate submission data against the schema
    Returns tuple (is_valid, error_message)
    """
    try:
        validate(instance=data, schema=submission_schema)
        return None  # No validation errors
    except ValidationError as e:
        return str(e)  # Return validation error message