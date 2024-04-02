# Zip Files Transfer and Automated Data Loading to Data Warehouse

### Overview:
In this scenario, users frequently receive numerous zipped files containing CSV data, sourced from the enterprise ecosystem. The primary objective is to securely transfer this data into an S3 bucket, serving as the data layer. The workflow involves unzipping each file and converting its contents into the Parquet format, optimizing it for downstream analysis. Additionally, the processed data should seamlessly populate a data warehouse, consolidating it into a unified table for cohesive analysis.
![My Remote Image](https://i.imgur.com/3ks2RoK.png)

# Content
- [Introduction]( )
- [Prerequiste]( )
- [S3 Bucket]( )
- [AWS Tranfer for SFTP]( )
- [Lambda Function Setup for Unzipping Files and Data Movement]( )
- [Glue Job Setup for Converting Files into Parque format]( )
- [Snowflake - Storage Integration, SQS to Snowpipe and Table]( )
- [Result]( )
<br/><br/>

### Prerequiste
This project requires the utilization of an AWS account for cloud services, Snowflake as the designated data warehouse, and WinSCP serving as the interface for file transfer. Additionally, WSL (Windows Subsystem for Linux) is employed to enable Linux command usage within the Windows operating system.

### S3 Bucket
The bucket contains 3 folders. 
- **Landing** is for the storage of the zipped files uploaded via SFTP. 
- **Curated** is for the storage of the file unzipped from the lambda functions.
- **Publish** is for the storage of the files converted from CSV to Parquet format that ready to be consumed by Snowpipe.


### AWS Tranfer for SFTP
Although we can directly interact with S3, AWS tranfer provide a seamlessly integrate with existing workflows. If your organization or applications already use these protocols for file transfer, it allows you to continue using them while storing files directly in Amazon S3 or Amazon EFS. It also centralizes the management like users, policies, network, keys, etc, as well as allowing the file I/O monitor.

To provide a interface for tranfering the file into S3 landing layer, we set up a SFTP server in AWS transfer. 
![My Remote Image](https://i.imgur.com/PH3EU51.png)

Then an user is created added into the server. The user is granted with the role having the privileage to interact with S3 bucket. The user is restricted to landing layer only so that he/she is not able to interact with other layers.
![My Remote Image](https://i.imgur.com/renMJfx.png)


The SSH key is set up via `ssh-keygen -t rsa` in the project folder. (The key in the following demostration will be all removed.)
![My Remote Image](https://i.imgur.com/BeUjTH2.png)

SSH key can be found in the <file_name>.pub, which can be simply shown via `cat <file_name>.pub`. Then the public key is added to the user.
![My Remote Image](https://i.imgur.com/XIzjYrD.png)
![My Remote Image](https://i.imgur.com/WcxfESY.png)

To connect the local system to AWS transfer, check out the endpoint of the AWS transfer server. Open WinSCP, input the enpoint and the username, as well as browsing the pivate key file created in previous step.
![My Remote Image](https://i.imgur.com/M5CPfvd.png)
![My Remote Image](https://i.imgur.com/H0hy5aT.png)
![My Remote Image](https://i.imgur.com/qIAQg4p.png)

From now on, once the files are dragged from left (local system) to right (remote), the files will be transfered to S3 landing layer. 

![My Remote Image](https://i.imgur.com/p85NcT5.png)
![My Remote Image](https://i.imgur.com/8EVlVVl.png)

### Lambda Function Setup for Unzipping Files and Data Movement
Create a Python Lambda function to unzip files from the Landing layer and transfer them to the Curated layer within an S3 bucket. The function has a 5-minute timeout and is granted an IAM role with the following policies
- AmazonS3FullAccess: for accessing S3 buckets
- AWSGlueConsoleFullAccess: for alowing the trigger Glue job within the funciton
- AWSLambdaBasicExecutionRole: for allowing lambda execution and cloudwatch
![My Remote Image](https://i.imgur.com/Po1GCvf.png)
![My Remote Image](https://i.imgur.com/8wxlh7n.png)

An S3 trigger is added so that once files are uploaded into landing layer, lambda function is triggered.
![My Remote Image](https://i.imgur.com/4RQWgOQ.png)
![My Remote Image](https://i.imgur.com/IzRCXGd.png)

### Glue Job Setup for Converting Files into Parque format
The Lambda function initiates the execution of a Glue job, with the IAM role attached enabling the access to the designated S3 bucket. To bolster its capabilities in handling potentially large influxes of files, the Glue job's maximum concurrency is increased. This enhancement ensures the job's agility in swiftly managing and processing substantial volumes of incoming files.
![My Remote Image](https://i.imgur.com/9hgONtL.png)

### Snowflake - Storage Integration, SQS to Snowpipe and Table
The linkage between S3 and Snowflake is established using the method outlined in https://docs.snowflake.com/en/user-guide/data-load-s3-config-storage-integration. Once all components—Storage Integration, stage, Snowpipe, and table—are set up, along with the SQS channel configuration, the Parquet files generated by Glue in the S3 publishing layer are directed to a designated Snowflake stage. These Parquet files are then automatically ingested via Snowpipe, facilitating the seamless loading of all data into a consolidated large table within Snowflake.


For the details, please refers to official documentation and the snowflake SQL in the script folder. Here is the overview of steps:
1.  created an IAM role, and attached the policy to the role with the access right to S3 bucket
2. Record the Role ARN value located on the role and build the storage integration specifying the ARN and S3 bucket path
```
CREATE STORAGE INTEGRATION <integration_name>
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = '<iam_role>'
  STORAGE_ALLOWED_LOCATIONS = ('s3://<bucket>/<path>/', 's3://<bucket>/<path>/')
  [ STORAGE_BLOCKED_LOCATIONS = ('s3://<bucket>/<path>/', 's3://<bucket>/<path>/') ]
```
3. create Trust relationships in the IAM role with the policy, specifying the `snowflake_user_arn` and `snowflake_external_id`, which can be obtained via `DESC INTEGRATION sf_storage_integration;`:
```
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "AWS": "<snowflake_user_arn>"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "<snowflake_external_id>"
        }
      }
    }
  ]
}
```
4. Create the table with the decided schema and file_format (parque)
5. Create an External Stage with the storage integration
6. Create an snowpipe to load the stage data into the designated table
7. Create the event notification within the S3 bucket. Select SQS queue and input its arn, obtained from `show pipes;` in Snowflake
![My Remote Image](https://i.imgur.com/ESi6Uhl.png)


### Result
Once the zipped files are uploaded, the files are processed and uploaded to the corresponding bucket folders. The data in all parque files will be consolidated in the designated snowflake table for further analysis.
![My Remote Image](https://i.imgur.com/vqE68ex.png)
