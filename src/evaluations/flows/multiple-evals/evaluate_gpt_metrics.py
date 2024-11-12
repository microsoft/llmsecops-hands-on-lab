from promptflow.core import tool
from promptflow.connections import AzureOpenAIConnection
from utils import get_openai_parameters
from utils import sdk_compute_metrics, parse_sdk_output
from constants import Metric


@tool
def evaluate_gpt_metrics(question: str,
                         answer: str,
                         context: str,
                         ground_truth: str,
                         connection: AzureOpenAIConnection,
                         deployment_name: str,
                         valid_metrics: dict) -> dict:
    y_pred = [answer]
    y_test = [ground_truth]

    openai_params = get_openai_parameters(connection,
                                          deployment_name)

    metrics_config = {
        "openai_params": openai_params,
        "questions": [question],
        "contexts": [context]
    }
    metrics = []
    for metric in Metric.QUALITY_METRICS:
        valid_input = valid_metrics[metric]
        sdk_metric = metric not in [
            Metric.GPTGroundedness,
            Metric.F1Score]
        if sdk_metric and valid_input:
            metrics.append(metric)
    if len(metrics) == 0:
        return None

    output = sdk_compute_metrics(
        task_type="qa",
        y_test=y_test,
        y_pred=y_pred,
        metrics=metrics,
        metrics_config=metrics_config
    )

    result = parse_sdk_output(output)

    return result
