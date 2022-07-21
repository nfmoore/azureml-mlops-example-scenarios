# Batch Endpoint Example Scenario

## Potential use cases

This approach is best suited for:
- High throughput scenarios
- Enriching data residing in a data lake at a pre-defined frequency

## Workflow

A high-level workflow for batch model deployment using Azure Machine Learning Batch Endpoints based on MLOps principles and practices is outlined below. This appraoch illistrates each of the main tasks that are executed  in Development, Staging, and Production environments orchastrated via GitHub Actions.

![design](./images/batch-endpoint.png)

## Implementation walkthrough

### Prerequisites

Before implementing this pattern, you need to:

- Azure subscription (contributor or owner)
- GitHub account
- Azure Machine Learning workspace

### Steps

```bash
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
```

```bash
az ml environment create -f employee-attrition/environments/train.yml
```

```bash
az ml environment create -f employee-attrition/environments/score.yml
```

```bash
az ml job create -f employee-attrition/pipelines/model_development.yml
```

```bash
az ml batch-endpoint create -f employee-attrition/deploy/batch/endpoint.yml
```

```bash
az ml batch-deployment create -f employee-attrition/deploy/batch/deployment.yml
```

## Related resources

You might also find these references useful:

- [Use batch endpoints for batch scoring](https://docs.microsoft.com/en-us/azure/machine-learning/how-to-use-batch-endpoint)
