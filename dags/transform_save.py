from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from pendulum import datetime
from airflow.models.param import Param
from include.universities.tasks import Task


@dag(
    start_date=datetime(2023, 4, 1),
    schedule_interval=None,
    catchup=False,
    render_template_as_native_obj=True,
    params={"country": Param("Undefined!", type="string")},
    tags=['university']
)

def transformation_savings():
    
    def get_params(**context):
        country = context["params"]["country"]
        print(f"Processing transformation of {country}")
        return country  

    transform_task = PythonOperator(
        task_id='get_params',
        python_callable=get_params,
        provide_context=True,
        do_xcom_push=True
    )
    
    get_university_details = PythonOperator(
        task_id='get_university_details',
        python_callable=Task._get_university_details,
        op_kwargs={'country': "{{ ti.xcom_pull(task_ids='get_params') }}"},
        do_xcom_push=True
    )
    
    save_university = PythonOperator(
        task_id='save_university',
        python_callable=Task._save_university,
        op_kwargs={'country': "{{ ti.xcom_pull(task_ids='get_params') }}" , 'university': '{{ task_instance.xcom_pull(task_ids="get_university_details")}}'},
        do_xcom_push=True     
    )

    clean_and_save_to_bq = DockerOperator(
        task_id='clean_and_save_to_bq',
        image='lc-app',
        container_name='university',
        api_version='auto',
        auto_remove=True,
        docker_url='tcp://docker-proxy:2375',
        network_mode='container:spark-master',
        tty=True,
        xcom_all=False,
        mount_tmp_dir=False,        
        environment={     
         'PAYLOAD': '{{task_instance.xcom_pull(task_ids="get_university_details")}}'
        },
        command="python3 main.py"          
    )
    
    transform_task >> get_university_details >> save_university >> clean_and_save_to_bq

transformation_savings()
