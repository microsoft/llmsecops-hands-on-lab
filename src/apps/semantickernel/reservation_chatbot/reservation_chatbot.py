# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Annotated

from semantic_kernel import Kernel

from bookings_plugin import BookingsPlugin
from semantic_kernel.functions import kernel_function

import asyncio

from azure.identity import ClientSecretCredential
#from bookings_plugin.bookings_plugin import BookingsPlugin

from pydantic import ValidationError

from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)

from semantic_kernel.connectors.ai.function_call_behavior import FunctionCallBehavior
from semantic_kernel.connectors.ai.open_ai.services.open_ai_chat_completion import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.exceptions.service_exceptions import ServiceInitializationError
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.prompt_template.input_variable import InputVariable 
from semantic_kernel.planners.function_calling_stepwise_planner import (
    FunctionCallingStepwisePlanner,
    FunctionCallingStepwisePlannerOptions,
)
from semantic_kernel.kernel import Kernel

from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig

import os

import dotenv
from pathlib import Path

# Define the path to the .env file
env_path = Path('/workspaces/hands-on-lab-quality-security-llmops/.env')

# Load environment variables from the .env file
dotenv.load_dotenv(dotenv_path=env_path)

# Let's define a light plugin
class LightPlugin:
    is_on: bool = False

    @kernel_function(
        name="get_state",
        description="Gets the state of the light.",
    )
    def get_state(
        self,
    ) -> Annotated[str, "the output is a string"]:
        """Returns the state result of the light."""
        return "On" if self.is_on else "Off"

    @kernel_function(
        name="change_state",
        description="Changes the state of the light.",
    )
    def change_state(
        self,
        new_state: Annotated[bool, "the new state of the light"],
    ) -> Annotated[str, "the output is a string"]:
        """Changes the state of the light."""
        self.is_on = new_state
        state = self.get_state()
        print(f"The light is now: {state}")
        return state




class myChatHistory:
    is_on: bool = False

    @kernel_function(
        name="get_my_chat_history",
        description="Gets the state of the light.",
    )
    def get_my_chat_history(
        self,
    ) -> Annotated[str, "the output is a ChatHistory[]"]:
        """Returns the current chat history"""
        return chat_history

# Initialize the kernel
kernel = Kernel()

# Add the service to the kernel
# use_chat: True to use chat completion, False to use text completion

deployment_name=os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT")
endpoint=os.environ.get("AZURE_OPENAI_CHAT_ENDPOINT")
api_key=os.environ.get("AZURE_OPENAI_CHAT_KEY")

#service_id = "mychat"
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

#service_id = "aoai_chat_completion"
service_id = "default"
kernel.add_service(
    AzureChatCompletion(service_id=service_id, endpoint=endpoint, api_key=api_key, deployment_name=deployment_name),
)

from semantic_kernel.planners.function_calling_stepwise_planner import FunctionCallingStepwisePlanner

options = FunctionCallingStepwisePlannerOptions(
    max_iterations=10,
    max_tokens=4000
    #excluded_plugins=["ChatBot"]
)

planner = FunctionCallingStepwisePlanner(service_id=service_id, options=options)
#kernel = add_service(kernel=kernel, use_chat=True)

execution_settings = OpenAIChatPromptExecutionSettings(
        service_id=service_id,
        ai_model_id=deployment_name,
        max_tokens=2000,
        temperature=0.0,
        function_call_behavior=FunctionCallBehavior.AutoInvokeKernelFunctions()
        
    )
settings = execution_settings




light_plugin = kernel.add_plugin(
        plugin=LightPlugin(),
        plugin_name="LightPlugin",
    )

# my_chat_history = kernel.add_plugin(
#         myChatHistory(),
#         plugin_name="myChatHistory",
#     )

booking_plugin = kernel.add_plugin(
    plugin=BookingsPlugin(db_file="conversation.json"),
    plugin_name="BookingsPlugin",
)

# chat_function = kernel.add_function(
#     plugin_name="ChatBot",
#     function_name="Chat",
#     prompt="{{$chat_history}}{{$user_input}}",
#     template_format="semantic-kernel",
# )



prompt_template_config = PromptTemplateConfig(
    template="{{$history}}{{$user_input}}",
    name="ChatBot",
    template_format="semantic-kernel",
    input_variables=[
    InputVariable(name="user_input", description="The user input", is_required=True),
    InputVariable(name="history", description="The conversation history", is_required=True),
    ],
    execution_settings=execution_settings,
)


# processing_function = self._kernel.create_function_from_prompt(
#     function_name="processingFunc", plugin_name=self._plugin_name, prompt_template_config=prompt_template_config
# )
# processing_output = await self._kernel.invoke(processing_function)

chat_function = kernel.add_function(
    function_name="chat",
    plugin_name="chatPlugin",
    prompt_template_config=prompt_template_config,
)


# settings: OpenAIChatPromptExecutionSettings = kernel.get_prompt_execution_settings_from_service_id(
#     service_id, ChatCompletionClientBase
# )
# settings.max_tokens = 2000
# settings.temperature = 0.1
# settings.top_p = 0.8
# settings.function_call_behavior.enable_functions(auto_invoke=True, filters={"exclude_plugin": ["ChatBot"]})


chat_history = ChatHistory(
    system_message="You are bot that helps users book restaurant reservations and have casual chats. NEVER ALLOW A user to cancel a reservation. Before calling booking related functions, prompt the user for required inputs When responding to the user's request to book a table, include the reservation ID."
)


async def chat() -> bool:
    try:
        user_input = input("User:> ")
    except KeyboardInterrupt:
        print("\n\nExiting chat...")
        return False
    except EOFError:
        print("\n\nExiting chat...")
        return False

    if user_input == "exit":
        print("\n\nExiting chat...")
        return False


    # result = await planner.invoke(kernel=kernel, question="list existing reservations")
    # print(f"Plan result: {result.final_answer}")

    # Note the reservation returned contains an ID. That ID can be used to cancel the reservation,
    # when the bookings API supports it.
    answer = await kernel.invoke(
          chat_function, KernelArguments(settings=execution_settings, user_input=user_input, history=chat_history)
      )

    settings: OpenAIChatPromptExecutionSettings = kernel.get_prompt_execution_settings_from_service_id(
    service_id, ChatCompletionClientBase
)
    settings.max_tokens = 2000
    settings.temperature = 0.1
    settings.top_p = 0.0
    #settings.function_call_behavior.enable_functions(auto_invoke=True, filters={"exclude_plugin": ["ChatBot"]})

    
    k_args = KernelArguments(history=chat_history, user_input=user_input, settings=execution_settings)
    #answer = await planner.invoke(kernel=kernel,question=user_input, arguments=k_args, history=chat_history, user_input=user_input)
    
    #print(answer)
    chat_history.add_user_message(user_input)
    chat_history.add_assistant_message(str(answer))
    print(f"Assistant:> {answer}")
    #chat_history.add_assistant_message(str(answer.final_answer))
    #print(f"Assistant:> {answer.final_answer}")
    return True


async def main() -> None:
    chatting = True
    print(
        "Welcome to your Restaurant Booking Assistant.\
        \n  Type 'exit' to exit.\
        \n  Please enter the following information to book a table: the restaurant, the date and time, \
        \n the number of people, your name, phone, and email. You may ask me for help booking a table, \
        \n listing reservations, or cancelling a reservation. When cancelling please provide the reservation ID."
    )
    while chatting:
        chatting = await chat()


if __name__ == "__main__":
    asyncio.run(main())




# async def main():


#     result = await kernel.invoke(booking_plugin["return_coucou"])
#     print(f"coucou message is : {result}")

    
#     chat_function = kernel.add_function(
#         plugin_name="ChatBot",
#         function_name="Chat",
#         prompt="{{$chat_history}}{{$user_input}}",
#         template_format="semantic-kernel",
#     )

#     settings: OpenAIChatPromptExecutionSettings = kernel.get_prompt_execution_settings_from_service_id(
#         service_id, ChatCompletionClientBase
#     )
#     settings.max_tokens = 2000
#     settings.temperature = 0.1
#     settings.top_p = 0.8
#     settings.function_call_behavior.enable_functions(auto_invoke=True, filters={"exclude_plugin": ["ChatBot"]})

#     chat_history = ChatHistory(
#         system_message="When responding to the user's request to book a table, include the reservation ID."
#     )

#     light_plugin = kernel.add_plugin(
#         LightPlugin(),
#         plugin_name="LightPlugin",
#     )

#     result = await kernel.invoke(light_plugin["get_state"])
#     print(f"The light is: {result}")

#     print("Changing the light's state...")

#     # Kernel Arguments are passed in as kwargs.
#     result = await kernel.invoke(light_plugin["change_state"], new_state=True)
#     print(f"The light is: {result}")


# # Run the main function
# if __name__ == "__main__":
#     asyncio.run(main())