import boto3
from zipfile import ZipFile

import os
import json
import uuid


myuuid = str(uuid.uuid4()).replace('-','')
glue_job_name='testsftpcsvtoparquet'


def lambda_handler(event, context):
    print("start the lambda")
    
    # TODO implement
    for record in event['Records']:
        
        # retrieve the S3 file name
        file_name_with_directory = record['s3']['object']['key']
        file_name = record['s3']['object']['key'].split('/')[1]
        bucketName = record['s3']['bucket']['name']
        
        print(record['s3']['object']['key'].split('/'))
        print("File Name : ",file_name)
        print("File Name with directory: ",file_name_with_directory)
        print("Bucket Name : ",bucketName)
        
        local_file_full_name='/tmp/{}'.format(file_name)
        print("local file full Name : ",local_file_full_name)
        
        
        #download the file from S3 landing zone
        s3 = boto3.client('s3')
        s3.download_file(bucketName, file_name_with_directory, local_file_full_name)
        print("File downloaded successfully")
        
        #extract the zip file
        with ZipFile(local_file_full_name, 'r') as f:
            #extract in current directory
            f.extractall('/tmp/unzip{}'.format(myuuid))
        
        # for each unzipped file, put them into S3 curated layer    
        file_names=''
        for filename in os.listdir('/tmp/unzip{}'.format(myuuid)):
            f = os.path.join('/tmp/unzip{}'.format(myuuid), filename)
            print("File Name : ",f)
            s3.upload_file(f, bucketName, 'curated/{}'.format(filename))
            os.remove(f)
            file_names=file_names+','+'s3://{}/curated/{}'.format(bucketName,filename)
        print("Files after unzip :", file_names)
        
        
        #trigger glue job and pass the file name to glue variable
        glue=boto3.client('glue');
        response = glue.start_job_run(JobName = glue_job_name, Arguments={"--VAL1":file_names[1:]})
        print("Glue Job trigger response : ",response)
        
        
        return {
            'statusCode': 200,
            'body': json.dumps('Hello from Lambda!')
        }