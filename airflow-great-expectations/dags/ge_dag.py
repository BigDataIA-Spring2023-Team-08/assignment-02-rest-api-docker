import os
from airflow.models import DAG
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.types.base import (
    DataContextConfig,
    CheckpointConfig
)

ge_root_dir = 'ge/great_expectations'


dag = DAG(
    dag_id="ge_dag",
    schedule="0 0 * * *",   # https://crontab.guru/
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
    tags=["great_expectations", "s3"],
    # params={"test":"value"},
    params=user_input,
)

with dag:
    ge_goes18_checkpoint_pass = GreatExpectationsOperator(
        task_id="task_goes18_checkpoint",
        data_context_root_dir=ge_root_dir,
        checkpoint_name="goes18_checkpoint_v0.1"
    )
    ge_nexrad_checkpoint_pass = GreatExpectationsOperator(
        task_id="task_nexrad_checkpoint",
        data_context_root_dir=ge_root_dir,
        checkpoint_name="nexrad_checkpoint_v0.2",
        trigger_rule="all_done"
    )

    ge_goes18_checkpoint_pass >> ge_nexrad_checkpoint_pass
