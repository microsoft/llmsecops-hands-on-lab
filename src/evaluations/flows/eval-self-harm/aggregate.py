
from typing import List

from promptflow.core import log_metric, tool

from collections import defaultdict

@tool
def aggregate(processed_results: List[dict]):
    """
    This tool aggregates the processed result of all lines and calculate the accuracy. Then log metric for the accuracy.

    :param processed_results: List of the output of line_process node.
    """

    # Add your aggregation logic here
    #print(processed_results)

    # Aggregate the results of all lines and calculate the accuracy
    #aggregated_result = round((processed_results.count("Safe") / len(processed_results)), 2)

    # Log metric the aggregate result
    #log_metric(key="mysafety", value=aggregated_result)

    # Initialize a dictionary to store counts of each violence level
    violence_counts = defaultdict(int)

    # Count the occurrences of each violence level
    for result in processed_results:
        violence_counts[result['self_harm']] += 1

    # Calculate and log metrics for each violence level
    output_dict = {}
    for violence_level, count in violence_counts.items():
        aggregated_result = round(count / len(processed_results), 2)
        log_metric(key=f"self_harm_{violence_level}", value=aggregated_result)
        output_dict[f"self_harm_{violence_level}"] = aggregated_result

    return output_dict
