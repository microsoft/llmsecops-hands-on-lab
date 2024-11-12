# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import List

from promptflow.core import log_metric, tool

from collections import defaultdict

@tool
def aggregate(processed_results: List[dict]):
    output_dict = {}
    keys = ['hate_unfairness', 'sexual', 'self_harm', 'violence']
    levels = ['Very low', 'Low', 'Medium', 'High', 'Very high']
    unprocessed_items = 0

    for result in processed_results:
        if result is None:
            unprocessed_items += 1
            continue
        for key in keys:
            for level in levels:
                if result[key] == level:
                    aggregated_result = sum([1 for item in processed_results if item[key] == level])
                    if aggregated_result > 0:
                        log_metric(key=f"{key}_{level}", value=aggregated_result)
                        output_dict[f"{key}_{level}"] = aggregated_result

    output_dict['unprocessed_items'] = unprocessed_items
    return output_dict

