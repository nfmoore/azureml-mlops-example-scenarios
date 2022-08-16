# imports
import os
from argparse import ArgumentParser, Namespace
from datetime import datetime, timedelta, timezone

import pandas as pd
from azure.identity import ManagedIdentityCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus


def main(args: Namespace) -> None:
    # setup log analytics client
    client_id = os.environ.get('DEFAULT_IDENTITY_CLIENT_ID')
    credential = ManagedIdentityCredential(client_id=client_id)
    client = LogsQueryClient(credential)

    # specify query window
    end_time = datetime.now(timezone.utc)
    start_time = (end_time - timedelta(days=args.number_of_previous_days))

    # create query
    log_analytics_query = f"""
        AmlOnlineEndpointConsoleLog
        | where Message has 'online/{args.model_name}/{args.model_version}'and Message has 'InputData'
        | project TimeGenerated, ResponsePayload=split(Message, '|')
        | project TimeGenerated, InputData=parse_json(tostring(ResponsePayload[-1])).data
        | project TimeGenerated, InputData=parse_json(tostring(InputData))
        | mv-expand InputData
        | evaluate bag_unpack(InputData)
    """

    # query log analytics workspace
    df_export = query_workspace(
        client, args.log_analytics_workspace_id, log_analytics_query, start_time, end_time)

    # define file name and path
    file_name = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    file_path = f"{args.prepared_data_dir}/employee-attrition/inference/online"

    # create directories if they do not exist
    os.makedirs(file_path, exist_ok=False)

    # write data to datastore
    df_export.to_csv(f"{file_path}/{file_name}.csv", index=False)


def query_workspace(
    client: LogsQueryClient,
    log_analytics_workspace_id: str,
    log_analytics_query: str,
    start_time: datetime,
    end_time: datetime
) -> pd.DataFrame:

    # query log analytics workspace
    response = client.query_workspace(
        workspace_id=log_analytics_workspace_id,
        query=log_analytics_query,
        timespan=(start_time, end_time)
    )

    # extract data from response for both partial and successful scenarios
    if response.status == LogsQueryStatus.PARTIAL:
        error = response.partial_error
        data = response.partial_data
        print(f"Partial error: {error.message}")

    else:
        data = response.tables

    # convert data to pandas dataframe
    for table in data:
        df = pd.DataFrame(data=table.rows, columns=table.columns)

    return df


def parse_args() -> Namespace:
    # setup arg parser
    parser = ArgumentParser("export")

    # add arguments
    parser.add_argument("--model_name", type=str)
    parser.add_argument("--model_version", type=str)
    parser.add_argument("--prepared_data_dir", type=str)
    parser.add_argument("--log_analytics_workspace_id", type=str)
    parser.add_argument("--number_of_previous_days", type=int)

    # parse args
    args = parser.parse_args()

    return args


if __name__ == "__main__":
    # parse args
    args = parse_args()

    # run main
    main(args)
