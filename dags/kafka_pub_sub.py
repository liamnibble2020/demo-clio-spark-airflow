from airflow.decorators import dag, task
from airflow.providers.apache.kafka.operators.produce import ProduceToTopicOperator
from airflow.providers.apache.kafka.operators.consume import ConsumeFromTopicOperator
from airflow.hooks.base import BaseHook
from airflow.sensors.base import PokeReturnValue
from datetime import datetime
import json
import requests

COUNTRY = ["Australia", "Bangladesh", "China"]
KAFKA_TOPIC = "country"
def producer():    
    yield (
        json.dumps("country"),
        json.dumps(
            {
                "date": datetime.now().isoformat(),
                "country": COUNTRY,
                "api_message": f"API connection is good, go ahead collect universities in this country",
            }
        ),
    )

 
    
def consumer(message):   
    key = json.loads(message.key())
    message_content = json.loads(message.value())
    country = message_content["country"]
    api_message = message_content["api_message"]
    print(
        f"Message #{key}: {api_message}: {country}"
    )
   

    
@task.sensor(poke_interval=30, timeout=300, mode="poke")
def is_api_available() -> PokeReturnValue:
    api = BaseHook.get_connection("free_api")
    url = f"{api.host}{api.extra_dejson['endpoint']}"
    response = requests.get(url, headers=api.extra_dejson['headers'])
    condition = response.status_code == 200
    return PokeReturnValue(
            is_done=condition,
            xcom_value=response.json() if condition else None
        )   
  
@dag(
    start_date=datetime(2023, 4, 1),
    schedule=None,
    catchup=False,
    render_template_as_native_obj=True,   
    tags=['university']
)
def kakfa_university():
    check_api = is_api_available()      

    country_producer = ProduceToTopicOperator(
        task_id="country_producer",
        kafka_config_id="kafka_default",
        topic=KAFKA_TOPIC,
        producer_function=producer,       
        poll_timeout=10,
    )

    country_consumer = ConsumeFromTopicOperator(
        task_id="country_consumer",
        kafka_config_id="kafka_default",      
        topics=[KAFKA_TOPIC],
        apply_function=consumer,    
        poll_timeout=20,
        max_messages=1000,        
    )

    check_api >> country_producer >> country_consumer


kakfa_university()