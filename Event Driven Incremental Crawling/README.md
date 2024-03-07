# Event Driven Incremental Crawling

## Overview:
In this project, the data stored in the datawarehouse (Snowfalke) have to be moved to S3 by partitions. Once the data are uploaded to S3 bucket, there is an event triger which sends message to SNS for messaging fanout, of which one of the message stream will go into SQS queue. Every Glue crawler is runned (on demand or schedule), it will incrementally crawling all the new partitions uploaded in the S3 instead of recrawling whole S3 bucket, which saves the time and computational cost. The use case can be applied to:
- **Backup and Archiving**: Storing data in S3 ensures a backup of your data in a durable and secure manner, enabling easy retrieval if needed.
- **Data Sharing and Collaboration**: S3 facilitates sharing data across different platforms or with external stakeholders by providing a centralized location accessible to authorized users.
- **Data Transformation or Processing**: It might be necessary to perform further transformations, analyses, or processing on the data stored in S3 using other tools or services.
- **Cost Optimization**: S3 offers cost-effective storage solutions, and moving data back can optimize costs by utilizing different storage classes based on data access frequency and retrieval needs.
- **Integration with other Services**: S3 integrates with various AWS services, allowing seamless integration with other tools or applications for specific workflows or analyses.
![My Remote Image](https://i.imgur.com/V74TUPQ.png)

# Content
- [Requirement]( )
- [Stage 1: Setup the S3 and Event Services]( )
- [Stage 2: Setup Glue Crawler]( )
- [Stage 3: Setup Snowflake]( )
- [Stage 4: Run & Result]( )
<br/><br/>

### Requirement
This project requires the utilization of an AWS account for cloud services and Snowflake as the data warehouse.

## Stage 1: Setup the S3 and Event Services
1. Use the defulat setting, create S3 bucket as datalake, SQS (standard) and SNS topic (standard)
2. Create an IAM role for glue, with full access/control in Glue, SQS and S3 
3. Attach the access policy (as demostrated in the files) for 
    - SNS: to allow publishing messages from S3 
    - SQS: to allow full access by glue with the IAM role for glue, sending message from SNS
4. Create event notification in S3, where the event is triggered by object creation and send the messages to SNS
5. Create SNS subscription where messages are published to the designated SQS queue

## Stage 2: Setup Glue Crawler
1. Add the data source with the S3 bucket. Select Crawl based on events and input the designated SQS ARN
2. Use the IAM role for Glue previously created 
3. Choose the target database (create one if not exist). Select **Create a single schema for each S3 path** in the Advance Options
> If the option to Create a single schema for each S3 path isn't chosen, the data catalog will generate individual tables for each partition file within the S3 bucket.

![My Remote Image](https://i.imgur.com/lZvN0zd.png)
![My Remote Image](https://i.imgur.com/bmsYPj7.png)

## Stage 3: Setup Snowflake
1. Create database
2. Create table and insert data
3. Create file format (here I use parque)
4. Unloading data using `copy into` keyword with the file format and AWS credential

## Stage 4: Testing & Result
1. Insert data to the table. Unloading data using `copy into` keyword with the file format and AWS credential
![My Remote Image](https://i.imgur.com/3Y2AJkM.png)

2. The partition folders and files should be created automatically
![My Remote Image](https://i.imgur.com/54O2AkQ.png)

3. SQS queue should recieve the message from SNS (# = row inserted)
![My Remote Image](https://i.imgur.com/RCOYobE.png)

4. Run the crawler in Glue and check the table created in Data Catalog
![My Remote Image](https://i.imgur.com/a8aR6GS.png)
![My Remote Image](https://i.imgur.com/LZSU3F0.png)

5. View the table in Athena
![My Remote Image](https://i.imgur.com/zsHuyiQ.png)