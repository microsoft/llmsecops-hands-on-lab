from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection
from utils import get_openai_parameters
from utils import sdk_compute_metrics, parse_sdk_output
from constants import Metric


@tool
def call_gpt_groundedness(connection: AzureOpenAIConnection,
                          context: str,
                          answer: str,
                          deployment_name: str):
    y_pred = [answer]

    openai_params = get_openai_parameters(connection,
                                          deployment_name)

    metrics_config = {
        "openai_params": openai_params,
        "contexts": [context]
    }

    metrics = [Metric.GPTGroundedness]

    output = sdk_compute_metrics(
        task_type="qa",
        y_pred=y_pred,
        metrics=metrics,
        metrics_config=metrics_config
    )
    result = parse_sdk_output(output)
    return result
