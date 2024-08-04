from airflow.decorators import dag
from pendulum import datetime
from airflow.providers.apache.kafka.sensors.kafka import (
    AwaitMessageTriggerFunctionSensor,
)
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import json
import uuid


KAFKA_TOPIC = "country"
def listening(message):
    message_content = json.loads(message.value())
    print(f"Full message: {message_content}")
    date = message_content["date"]
    country = message_content["country"]   
    return date, country
        

def event_triggered_function(message, **context):    

    date = message[0]
    countries = message[1]
    for country in countries:
        print(
            f"Collecting universities in country {country} date: {date}"
        )        
        trigger = TriggerDagRunOperator(
            trigger_dag_id="transformation_savings",
            task_id=f"triggered_downstream_dag_{uuid.uuid4()}",
            wait_for_completion=True,  
            conf={
                "country": country
            },  
            poke_interval=20,
        )
        trigger.execute(context)
        print(f"Processing {country} is now completed!")


@dag(
    start_date=datetime(2023, 1, 1),
    schedule="@continuous",
    max_active_runs=1,
    catchup=False,
    render_template_as_native_obj=True,
    tags=['university']
)
def stream_listener():
    AwaitMessageTriggerFunctionSensor(
        task_id="kafka_listener",
        kafka_config_id="kafka_listener",
        topics=[KAFKA_TOPIC],      
        apply_function="stream_listener.listening",
        poll_interval=5,     
        poll_timeout=1,        
        event_triggered_function=event_triggered_function,
    )


stream_listener()
