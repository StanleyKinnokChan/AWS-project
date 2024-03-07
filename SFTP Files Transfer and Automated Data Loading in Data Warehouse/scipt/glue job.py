import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()

def main():
    print("start glue job")
    ## @params: [JOB_NAME]
    
#get the file variable
    args = getResolvedOptions(sys.argv, ["VAL1"])
    file_names=args['VAL1'].split(',')

#put file into spark df and convert into parquet
    df = spark.read.csv(file_names[0], header = True)
    df.repartition(1).write.mode('append').parquet("s3a://sftp-pipeline-use-case-demo/publish/")
main()