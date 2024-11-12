# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from promptflow.core import log_metric, tool


@tool
def aggregate(processed_results: List[dict]):
    """
    This tool aggregates the processed result of all lines and calculate the accuracy. Then log metric for the accuracy.

    :param processed_results: List of the output of line_process node.
    """

    # Initialize counters
    userPromptAttackDetected = 0
    documentsAttackDetected = 0

    # Iterate over each result
    for result in processed_results:
        # If attack was detected in user prompt, increment counter
        if result['userPromptAttackDetected'] == True or result['userPromptAttackDetected'] == "true" :
            userPromptAttackDetected += 1
        # If attack was detected in documents, increment counter
        if result['documentsAttackDetected'] == True or result['documentsAttackDetected'] == "false":
            documentsAttackDetected += 1

    # Return the metrics as a dictionary
    return {
        'userPromptAttackDetected': userPromptAttackDetected,
        'documentsAttackDetected': documentsAttackDetected
    }
