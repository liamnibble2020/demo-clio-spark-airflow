FROM openjdk:8-jdk-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y wget tar python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Spark
RUN wget -q http://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz && \
    tar xf spark-3.1.1-bin-hadoop3.2.tgz && \
    rm spark-3.1.1-bin-hadoop3.2.tgz && \
    mv spark-3.1.1-bin-hadoop3.2 /opt/spark

# Set environment variables
ENV JAVA_HOME /usr/local/openjdk-8
ENV SPARK_HOME /opt/spark
ENV PATH $PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV DATASET="dreamlogic"
ENV PROJECT_ID="off-net-dev"
ENV TABLE="dreamlogic.universities"
ENV ENDPOINT="http://host.docker.internal:9000"
ENV SPARK_APPLICATION_PYTHON_LOCATION="/app/main.py"
ENV ENABLE_INIT_DAEMON=false

# Install Python packages
COPY requirements.txt /app/requirements.txt
RUN pip3 install -r /app/requirements.txt

# Copy application files
COPY main.py /app/main.py
COPY off-net-dev-reload.json /app/off-net-dev-reload.json
# Set working directory
WORKDIR /app

ENV GOOGLE_APPLICATION_CREDENTIALS="/app/off-net-dev-reload.json"
# Default command
CMD ["python3", "main.py", "{{ task_instance.xcom_pull(task_ids='get_university_details') }}"]