# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from promptflow.core import tool
from azure.identity import DefaultAzureCredential
from promptflow.evals.evaluators import ViolenceEvaluator, SelfHarmEvaluator

from promptflow.evals.evaluators import ChatEvaluator, ContentSafetyChatEvaluator, ContentSafetyEvaluator

import os
import time
from promptflow.core import AzureOpenAIModelConfiguration

# Initialize Azure OpenAI Connection with your environment variables
# model_config = AzureOpenAIModelConfiguration(
#     azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
#     api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
#     azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT"),
#     api_version=os.environ.get("AZURE_OPENAI_API_VERSION"),
# )

model_config = AzureOpenAIModelConfiguration(
    azure_endpoint="https://yayacopilot.openai.azure.com",
    api_key="f738a296285f4c4e805d9e2900321757",
    azure_deployment="gpt-35-turbo",
    api_version="2024-02-01",
)



azure_ai_project = {
    "subscription_id": "0f4bda7e-1203-4f11-9a85-22653e9af4b4",
    "resource_group_name": "copilot",
    "project_name": "safetyeval2",
    "credential": DefaultAzureCredential(),
}



# Initialzing Violence Evaluator with project information
#violence_eval = ViolenceEvaluator(azure_ai_project)
#self_harm_eval = SelfHarmEvaluator(azure_ai_project)
safety_eval = ContentSafetyEvaluator(azure_ai_project)

@tool
def line_process(question: str, prediction: str, groundtruth: str):
    """
    This tool processes the prediction of a single line and returns the processed result.

    :param question: the user question of a single line.
    :param groundtruth: the groundtruth of a single line.
    :param prediction: the prediction of a single line.
    """

    # Define the number of retries
    retries = 3

    for i in range(retries):
        try:
            # Running Violence Evaluator on single input row
            #violence_score = violence_eval(question=question, answer=prediction)
            #self_harm_score = self_harm_eval(question=question, answer=prediction)
            safety_score = safety_eval(question=question, answer=prediction)
            #print(violence_score)

            return safety_score

        except Exception as e:
            print(f"Attempt {i+1} of {retries} failed with error: {e}")
            time.sleep(1)  # Wait for 1 second before retrying

    print("All attempts failed. Please check your credentials and try again.")
