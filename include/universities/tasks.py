from airflow.hooks.base import BaseHook
import requests
import json
import boto3


class Task:   
 
    def _get_university_details(country):      
        api = BaseHook.get_connection("free_api")
        url = f"{api.host}{api.extra_dejson['endpoint']}search?country={country}"  
        response = requests.get(url, headers=api.extra_dejson['headers'])    
        response_data = response.json()       
        if isinstance(response_data, list):
            filtered_data = [
                            {                                 
                                "alpha_two_code": item["alpha_two_code"],
                                "country": item["country"],
                                "name": item["name"]
                            } 
                            for item in response_data
                            ]
            return json.dumps(filtered_data)
        
    def _save_university(country,university):
        conn = BaseHook.get_connection("s3_bucket")
        aws_access_key = conn.login
        aws_secret_key = conn.password
        extra_config = conn.extra_dejson                  
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name="ap-northeast-1"
        )    
             
        response = s3_client.put_object(Bucket=extra_config.get('bucket_name'), Key=f'{country}.json', Body=json.dumps(university),ContentType='application/json')
        
        return {
            'status_code': response['ResponseMetadata']['HTTPStatusCode'],
            'bucket': extra_config.get('bucket_name'),
            'key': f'{country}.json'
        }
        
   