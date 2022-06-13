# azureml-mlops

```bash
az configure --defaults group=$GROUP workspace=$WORKSPACE location=$LOCATION
```

```bash
az ml env create -f employee-attrition/environments/train.yml
```

```bash
az ml job create -f employee-attrition/pipelines/model_development.yml
```

```bash
az ml online-endpoint create -f employee-attrition/environments/train.yml
```

```bash
az ml online-deployment create -f employee-attrition/environments/train.yml
```
