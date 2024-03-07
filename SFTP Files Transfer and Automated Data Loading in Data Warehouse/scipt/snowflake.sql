--drop database if exists
drop database if exists s3_to_snowflake;

--Database Creation 
create database if not exists s3_to_snowflake;

--Use the database
use s3_to_snowflake;

--create integration from AWS role
CREATE OR REPLACE STORAGE INTEGRATION sf_storage_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::459967084692:role/mysnowflakerole'
  STORAGE_ALLOWED_LOCATIONS = ('s3://sftp-pipeline-use-case-demo/');


--use the user id and external id to build trust relationshiop in AWS
DESC INTEGRATION sf_storage_integration;

--grant the privilege to role
GRANT CREATE STAGE ON SCHEMA public TO ROLE ACCOUNTADMIN;
GRANT USAGE ON INTEGRATION sf_storage_integration TO ROLE ACCOUNTADMIN;

--Table Creation
create or replace table s3_to_snowflake.PUBLIC.sales_table (
   Date          VARCHAR(50)
  ,Country       VARCHAR(50)
  ,City          VARCHAR(50)
  ,State_City  VARCHAR(50)
  ,Category      VARCHAR(50)
  ,Consumer      NUMERIC(30,3)
  ,Corporate     NUMERIC(30,0)
  ,"Home Office" NUMERIC(30,0)
  );
                                  
--create the file format
CREATE OR REPLACE FILE FORMAT sf_tut_parquet_format
  TYPE = parquet;

--create the external stage
create or replace stage s3_to_snowflake.PUBLIC.Snow_stage
url="s3://sftp-pipeline-use-case-demo/publish/" 
STORAGE_INTEGRATION = sf_storage_integration
file_format = sf_tut_parquet_format;

list @Snow_stage;

--test
create or replace pipe s3_to_snowflake.PUBLIC.for_sales_table
auto_ingest=true as 
copy into s3_to_snowflake.PUBLIC.sales_table
from 
(select
$1:Date::VARCHAR,
$1:Country::VARCHAR,
$1:City::VARCHAR,
$1:State_City::VARCHAR,
$1:Category::VARCHAR,
$1:Consumer::number,
$1:Corporate::number,
$1:Home_Office::number
from @s3_to_snowflake.PUBLIC.Snow_stage);


--use the noti channel in aws SQS
show pipes;

select * from s3_to_snowflake.PUBLIC.sales_table;