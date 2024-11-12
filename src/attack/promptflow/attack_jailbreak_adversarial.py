from promptflow.evals.synthetic import AdversarialSimulator

from azure.identity import DefaultAzureCredential

from typing import List, Dict, Any

import asyncio

azure_ai_project = {
    "subscription_id": "0f4bda7e-1203-4f11-9a85-22653e9af4b4",
    "resource_group_name": "copilot",
    "project_name": "safetyeval2",
    "credential": DefaultAzureCredential(),
}


import os
from openai import AzureOpenAI

async def function_call_to_your_endpoint(query: str, messages: List[Dict]) -> str:
    # Replace with your actual endpoint URL and key
    endpoint_url = os.getenv("AZURE_OPENAI_ENDPOINT")
    endpoint_url = "https://yayacopilot.openai.azure.com"
    key = os.getenv("AZURE_OPENAI_API_KEY")
    key = "f738a296285f4c4e805d9e2900321757"

    # Create a client using the AzureOpenAI
    client = AzureOpenAI(api_key=key, api_version="2024-02-01", azure_endpoint=endpoint_url)

    # Prepare the payload
    messages2 = [
        {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
        {"role": "user", "content": query}
    ]

    # Make the asynchronous POST request
    response = client.chat.completions.create(model="gpt-35-turbo", messages=messages)

    # Extract the content from the response
    response_content = response.choices[0].message.content

    return response_content.strip()



async def callback(
    messages: List[Dict],
    stream: bool = False,
    session_state: Any = None,
) -> dict:
    query = messages["messages"][0]["content"]
    context = None

    # Add file contents for summarization or re-write
    if 'file_content' in messages["template_parameters"]:
        query += messages["template_parameters"]['file_content']
    
    # Call your own endpoint and pass your query as input. Make sure to handle your function_call_to_your_endpoint's error responses.
    response = await function_call_to_your_endpoint(query, messages["messages"]) 
    
    # Format responses in OpenAI message protocol
    formatted_response = {
        "content": response,
        "role": "assistant",
        "context": {},
    }

    messages["messages"].append(formatted_response)
    return {
        "messages": messages["messages"],
        "stream": stream,
        "session_state": session_state
    }


from promptflow.evals.synthetic import AdversarialScenario

async def main():
    #scenario = AdversarialScenario.ADVERSARIAL_QA
    scenario = AdversarialScenario.ADVERSARIAL_CONVERSATION
    simulator = AdversarialSimulator(azure_ai_project=azure_ai_project)

    outputs_with_jailbreak = await simulator(
        scenario=scenario,  # required adversarial scenario to simulate
        target=callback,  # callback function to simulate against
        max_conversation_turns=3,  # optional, applicable only to conversation scenario
        max_simulation_results=1,  # optional
        jailbreak=True  # optional
    )

    outputs_without_jailbreak = await simulator(
        scenario=scenario,  # required adversarial scenario to simulate
        target=callback,  # callback function to simulate against
        max_conversation_turns=3,  # optional, applicable only to conversation scenario
        max_simulation_results=1,  # optional
        jailbreak=False  # optional
    )

    # By default simulator outputs json, use the following helper function to convert to QA pairs in jsonl format
    jsonl_data = outputs_with_jailbreak.to_eval_qa_json_lines()
    print(jsonl_data)
    with open('eval_data_jailbreak.jsonl', 'a+') as f:
        f.write(jsonl_data)
        print("The Adversarial conversation with jailbreak was saved to eval_data_jailbreak.jsonl")

    jsonl_data = outputs_without_jailbreak.to_eval_qa_json_lines()
    print(jsonl_data)
    with open('eval_data.jsonl', 'a+') as f:
        f.write(jsonl_data)
        print("The Adversarial conversation without jailbreak was saved to eval_data.jsonl")

# Call the main function
asyncio.run(main())
