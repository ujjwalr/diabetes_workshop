# This script populates the S3 bucket with transformed data that is read from RDS.
# Replace <S3 Bucket Name> with the name of the bucket created by the cloudformation script
# If you do not choose gluedatacatalog as the name of your database when creating the crawler, make sure to replace that name with your name of your database in this script.
# Make sure the database and table_name in the script are the same as the ones in the glue Database and tables 

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

datasource1 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_labs"
, transformation_ctx = "datasource1")
df1 = datasource1.toDF()
df1.show()

sqlContext.registerDataFrameAsTable(df1, "labs")

df_glucose = sqlContext.sql("SELECT PatientID ,min(LabValue) as minvalueglucose, LabType from labs group by PatientID,LabType having LabType='Glucose'")

df_hba1c = sqlContext.sql("SELECT PatientID ,max(LabValue) as maxvaluehba1c, LabType from labs group by PatientID,LabType having LabType='HBA1C'")

df_gfr = sqlContext.sql("SELECT PatientID ,min(LabValue) as minvaluegfr, LabType from labs group by PatientID,LabType having LabType='GFR'")


df_gfr.show()

df3=df0.join(df_glucose, df0.PatientID == df_glucose.PatientID).drop(df_glucose.PatientID).drop(df_glucose.LabType)
df4=df3.join(df_hba1c, df3.PatientID == df_hba1c.PatientID).drop(df_hba1c.PatientID).drop(df_hba1c.LabType)
df5=df4.join(df_gfr, df4.PatientID == df_gfr.PatientID).drop(df_gfr.PatientID).drop(df_gfr.LabType)

df5.show()
df5.count()

df_hashighhba1c=df5.withColumn('HasHighHba1c', F.when(df5.maxvaluehba1c > 7, 1).otherwise(0))
df_hasdiabeticretinopathy=df_hashighhba1c.withColumn('HasDiabeticRetinopathy', F.when(df_hashighhba1c.maxvaluehba1c > 9.5, 1).otherwise(0))
df_haskidneydisease=df_hasdiabeticretinopathy.withColumn('HasKidneyDisease', F.when(df_hasdiabeticretinopathy.minvaluegfr < 20, 1).otherwise(0))

df_haskidneydisease.show()

df_HBA1CCategory=df_haskidneydisease.withColumn('HBA1CCategory', F.when(df_haskidneydisease.maxvaluehba1c > 7.5, "high").
when(df_haskidneydisease.maxvaluehba1c.between(6.5, 7.5),"moderate").otherwise("ok"))

df_glucoseCategory=df_HBA1CCategory.withColumn('glucoseCategory', F.when(df_HBA1CCategory.minvalueglucose > 150, "high")
.when(df_HBA1CCategory.minvalueglucose.between(100, 150),"moderate").otherwise("ok"))



df_glucoseCategory.show()

df_final=df_glucoseCategory.select('PatientID','PatientGender','PatientRace','PatientEthnicity','HasHighHba1c','HasDiabeticRetinopathy'
,'HasKidneyDisease', 'glucoseCategory', 'HBA1CCategory')
df_final.show()
df_final.count()

datasink = glueContext.write_dynamic_frame.from_options(frame = dynamicframeout0, connection_type = "s3", connection_options = {"path": "s3://<S3 Bucket Name>/"}, format = "csv", transformation_ctx = "datasink")

datasink1 = glueContext.write_dynamic_frame.from_catalog(frame = dynamicframeout0, database = "gluedatacatalog", table_name = "source_diabetes_diabetesstudy", transformation_ctx = "datasink1")