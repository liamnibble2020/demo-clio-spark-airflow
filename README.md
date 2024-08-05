# `DEMO PROJECT for SPARK, AIRFLOW and KAFKA`

![Diagram](./images/clio.drawio.png)

# `How it works in local`

    Open Docker Desktop

    cd airflow
    astro dev start

    cd spark/notebooks/university
    docker build -t lc-app .

    Under dags/kafka_pub_sub.py add array of countries ex: ["Canada", "France"]

    In localhost:8080 unpause dags

    Wait for the stream_listener to be deffered status

    Run kafka_university

# `Overview`

    Check if the free Api is up
    Publish the array of countries
    Consume the message and iterate the countries pass as params
    	trigger the transform_save and await
    	 	transform_save
    			use params call API
    			get university details
    			save university to AWS S3
    			call spark transform unversity detaills adding fictitious number of students and date established
    			save to GCP BigQuery
