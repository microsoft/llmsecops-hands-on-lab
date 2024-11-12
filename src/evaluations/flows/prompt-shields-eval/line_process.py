# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from promptflow.core import tool


import requests
import json




@tool
def line_process(question : str, groundtruth: str, prediction: str):
    """
    This tool processes the prediction of a single line and returns the processed result.

    :param groundtruth: the groundtruth of a single line.
    :param prediction: the prediction of a single line.
    """

    # Add your line processing logic here
    #processed_result = "Correct" if groundtruth.lower() == prediction.lower() else "Incorrect"

    CONTENT_SAFETY_API_KEY = "5dda020dc12948c3b6820a2219912f32"
    endpoint = "https://yayasafetycontent.cognitiveservices.azure.com"
    headers = {
        'Ocp-Apim-Subscription-Key': CONTENT_SAFETY_API_KEY,
        'Content-Type': 'application/json'
    }

    data = {
    "userPrompt": question,
    "documents": [
        "Hi John, I hope you are doing well."
    ]
    }
    response = requests.post(f'{endpoint}/contentsafety/text:shieldPrompt?api-version=2024-02-15-preview', headers=headers, data=json.dumps(data), json=json.dumps(data))

    returned_dict = {}
    if response:
        
        toto = response.json()
        userPromptAttackDetected = toto["userPromptAnalysis"]["attackDetected"]
        documentsAttackDetected = any(doc["attackDetected"] for doc in toto["documentsAnalysis"])
        returned_dict["userPromptAttackDetected"] = userPromptAttackDetected
        returned_dict["documentsAttackDetected"] = documentsAttackDetected
        returned_dict["contentSafetyResponse"] = response.json()
    else:
        returned_dict = {}


    return returned_dict
