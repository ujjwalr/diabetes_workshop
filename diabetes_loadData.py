# This script populates the S3 bucket with transformed data that is read from RDS.
# Replace <S3 Bucket Name> with the name of the bucket created by the cloudformation script


import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.dynamicframe import DynamicFrame, DynamicFrameReader, DynamicFrameWriter, DynamicFrameCollection
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType

glueContext = GlueContext(SparkContext.getOrCreate())

datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_patients", transformation_ctx = "datasource0")
datasource0.printSchema()
df0 = datasource0.toDF()
df0.show()

datasource1 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_hba1c", transformation_ctx = "datasource1")
datasource1.printSchema()
df1 = datasource1.toDF()
df1.show()

datasource2 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_glucose", transformation_ctx = "datasource2")
datasource2.printSchema()
df2 = datasource2.toDF()
df2.show()


df3=df0.join(df1, df0.PatientID == df1.PatientID).drop(df1.PatientID)
df3.show()

df4=df3.join(df2, df3.PatientID == df2.PatientID).drop(df2.PatientID)
df4.show()

df_hba1c=df4.withColumn('hasHighHba1c', F.when(df4.avgvaluehba1c > 8, 1).otherwise(0))
df_hba1c.show()
print "Count: ", df_hba1c.count()

df_glucose=df_hba1c.withColumn('glucoseCategory', F.when(df_hba1c.avgvalueglucose < 70, "low").when(df_hba1c.avgvalueglucose.between(70, 100),"ok").when(df_hba1c.avgvalueglucose.between(101, 130),"high").otherwise("very high"))
df_glucose.show()

df_final=df_glucose.select('PatientID','PatientGender','PatientRace','PatientEthnicity','hasHighHba1c','glucoseCategory')
df_final.show()

dynamicframeout0 = DynamicFrame.fromDF(df_final, glueContext, "df_final")

datasink = glueContext.write_dynamic_frame.from_options(frame = dynamicframeout0, connection_type = "s3", connection_options = {"path": "s3://<S3 Bucket Name>/"}, format = "csv", transformation_ctx = "datasink")


