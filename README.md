# azureml-mlops

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
az ml online-endpoint create -f employee-attrition/deploy/online/endpoint.yml
```

```bash
az ml online-deployment create -f employee-attrition/deploy/online/deployment.yml
```

```bash
az ml batch-endpoint create -f employee-attrition/deploy/batch/endpoint.yml
```

```bash
az ml batch-deployment create -f employee-attrition/deploy/batch/deployment.yml
```
