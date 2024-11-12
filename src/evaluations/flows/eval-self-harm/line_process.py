# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from promptflow.core import tool
from azure.identity import DefaultAzureCredential
from promptflow.evals.evaluators import ViolenceEvaluator, SelfHarmEvaluator


azure_ai_project = {
    "subscription_id": "0f4bda7e-1203-4f11-9a85-22653e9af4b4",
    "resource_group_name": "copilot",
    "project_name": "safetyeval2",
    "credential": DefaultAzureCredential(),
}

# Initialzing Violence Evaluator with project information
violence_eval = ViolenceEvaluator(azure_ai_project)
self_harm_eval = SelfHarmEvaluator(azure_ai_project)

@tool
def line_process(question: str, prediction: str, groundtruth: str):
    """
    This tool processes the prediction of a single line and returns the processed result.

    :param question: the user question of a single line.
    :param groundtruth: the groundtruth of a single line.
    :param prediction: the prediction of a single line.
    """

    # Running Violence Evaluator on single input row
    violence_score = violence_eval(question=question, answer=prediction)
    self_harm_score = self_harm_eval(question=question, answer=prediction)
    #print(violence_score)

    return self_harm_score
