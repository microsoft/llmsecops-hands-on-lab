import constants
import numpy as np
import re
from promptflow.connections import AzureOpenAIConnection
from promptflow._utils.logger_utils import logger
from azureml.metrics import compute_metrics


def get_openai_parameters(connection: AzureOpenAIConnection,
                          deployment_name: str) -> dict:
    openai_params = {
        "api_version": connection['api_version'],
        "api_base": connection['api_base'],
        "api_type": "azure",
        "api_key": connection['api_key'],
        "deployment_id": deployment_name
    }
    return openai_params


def filter_metrics(selected_metrics):
    return [metric for metric in selected_metrics
            if selected_metrics[metric]]


def get_cred():
    from mlflow.tracking import MlflowClient
    import mlflow

    # check if tracking_uri is set. if False, return None
    if not mlflow.is_tracking_uri_set():
        return None

    mlflow_client = MlflowClient()
    cred = mlflow_client._tracking_client.store.get_host_creds()
    cred.host = cred.host\
                    .replace("mlflow/v2.0", "mlflow/v1.0")\
                    .replace("mlflow/v1.0", "raisvc/v1.0")
    return cred


def get_harm_severity_level(harm_score: int) -> str:
    HARM_SEVERITY_LEVEL_MAPPING = {constants.HarmSeverityLevel.VeryLow: [0, 1],
                                   constants.HarmSeverityLevel.Low: [2, 3],
                                   constants.HarmSeverityLevel.Medium: [4, 5],
                                   constants.HarmSeverityLevel.High: [6, 7]
                                   }
    if harm_score == np.nan or harm_score is None:
        return np.nan
    for harm_level, harm_score_range in HARM_SEVERITY_LEVEL_MAPPING.items():
        if harm_score >= harm_score_range[0] and\
           harm_score <= harm_score_range[1]:
            return harm_level.value
    return np.nan


def is_valid_string(input_string: str) -> bool:
    # if input_string contains any letter or number,
    # it is a valid string
    if not input_string:
        return False
    return bool(re.search(r'\d|\w', input_string))


def validate_score_range(score, score_range):
    return score >= score_range[0] and score <= score_range[1]


def sdk_compute_metrics(task_type,
                        y_pred,
                        metrics,
                        metrics_config,
                        y_test=None):
    use_chat_completion_api = True
    try:
        result = compute_metrics(
            task_type=task_type,
            y_test=y_test,
            y_pred=y_pred,
            metrics=metrics,
            use_chat_completion_api=use_chat_completion_api,
            **metrics_config)
        if result and "metrics" in result:
            for metric in metrics:
                field_name = "mean_" + metric
                if field_name in result["metrics"]:
                    metric_value = result["metrics"][field_name]
                    if not metric_value >= 0:
                        use_chat_completion_api = not use_chat_completion_api
                    break
        if use_chat_completion_api is False:
            result = compute_metrics(
                task_type=task_type,
                y_pred=y_pred,
                metrics=metrics,
                use_chat_completion_api=use_chat_completion_api,
                y_test=y_test,
                **metrics_config
                )
    except Exception:
        result = None

    # if result is empty or None or
    # result["artifacts"] is empty
    # set the score of metric per turn to np.nan
    set_dummy_result = (not result) or\
        ("artifacts" in result and not result["artifacts"])
    if set_dummy_result:
        for metric in metrics:
            error_message = "Failed to evaluate %s. " \
                % (metrics) + \
                "Please check deployment."
            logger.error(error_message)
        result = create_dummy_sdk_result(metrics)
    return result


def create_dummy_sdk_result(metrics: list) -> dict:
    if not metrics:
        return None
    dummy_result = {'artifacts': {},
                    'metrics': {}}
    for metric in metrics:
        dummy_result['artifacts'][metric] = [np.nan]
        dummy_result['metrics']['mean_' + metric] = np.nan
    return dummy_result


def parse_sdk_output(sdk_output: dict) -> dict:
    result = {}
    if not sdk_output:
        return result
    score_range = [
            constants.MetricRange.QUALITY_METRICS_MIN,
            constants.MetricRange.QUALITY_METRICS_MAX]
    if "artifacts" in sdk_output and sdk_output["artifacts"]:
        for metric in sdk_output["artifacts"].keys():
            try:
                score = float(sdk_output["artifacts"][metric][0])
                if not validate_score_range(score, score_range):
                    score = np.nan
            except Exception:
                logger.error("Failed to evaluate %s" % metric)
                score = np.nan
            result[metric] = score
    return result
