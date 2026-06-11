import sys
from pyspark.sql.functions import col
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import time

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
logger = glueContext.get_logger()
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
df = spark.read.json("s3://worldbank-pipeline-surya/bronze/*/*.json")
df = df.withColumn("country_id", col("country.id")) \
       .withColumn("country_name", col("country.value"))
       
df = df.withColumn("date", col("date").cast("integer"))
df = df.filter(col("value").isNotNull()) \
       .filter(col("country_id").rlike("^[A-Z]{2}$"))
df = df.drop("country", "unit", "obs_status", "decimal")

upload_start = time.time()

df.write \
  .mode("overwrite") \
  .partitionBy("date") \
  .parquet("s3://worldbank-pipeline-surya/silver/")

upload_elapsed = time.time() - upload_start
logger.info(f"S3 upload took {upload_elapsed:.2f} seconds")
print(f"S3 upload took {upload_elapsed:.2f} seconds")

job.commit()