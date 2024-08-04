import os
import random
import pandas
import pandas_gbq
import json
import findspark
findspark.init()
import pyspark 

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructType, StructField
from pyspark.sql.functions import col, expr, udf
from datetime import datetime, timedelta

def random_date():
    start_date = datetime(1975, 1, 1)
    end_date = datetime(2022, 12, 31)
    delta = end_date - start_date
    random_days = random.randrange(delta.days)
    random_date = start_date + timedelta(days=random_days)
    return random_date.strftime("%m-%d-%Y")

def random_students():
    return random.randint(3000, 5000)

def main():
  
    payload = os.getenv('PAYLOAD')   
    
    schema = StructType([
        StructField("alpha_two_code", StringType(), True),
        StructField("country", StringType(), True),
        StructField("name", StringType(), True)
    ])
        
    spark = SparkSession.builder.appName("test-spark").getOrCreate()
    
    rdd = spark.sparkContext.parallelize([payload])    

    df = spark.read.schema(schema).json(rdd)  
       
    random_date_udf = udf(random_date, StringType())
    random_students_udf = udf(random_students, IntegerType())
        
    df = df.withColumn("date_established", random_date_udf())
    df = df.withColumn("number_of_students", random_students_udf())
    df = df.withColumn("male", (col("number_of_students") * expr("rand()")).cast(IntegerType()))
    df = df.withColumn("female", col("number_of_students") - col("male"))
   
    data_collected = df.collect()
    for row in data_collected:
        print(row)  
        
    pandas_df = df.toPandas()   
 
    project_id = os.getenv("PROJECT_ID")  
    table_id = os.getenv("TABLE")
    
    try:
        pandas_gbq.to_gbq(pandas_df, table_id, project_id, if_exists="append")
        print("Data successfully saved to BigQuery")
    except Exception as e:
        print(f"An error occurred while saving to BigQuery: {e}")
    
if __name__ == "__main__":
    main()
