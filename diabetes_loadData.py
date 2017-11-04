# This script populates the S3 bucket with transformed data that is read from RDS.
# Replace <S3 Bucket Name> with the name of the bucket created by the cloudformation script
# If you do not choose gluedatacatalog as the name of your database when creating the crawler, make sure to replace that name with your name of your database in this script.


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

datasource3 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_gfr",
transformation_ctx = "datasource3")
datasource3.printSchema()
dfgfr = datasource3.toDF()
dfgfr.show()

df3=df0.join(df1, df0.PatientID == df1.PatientID).drop(df1.PatientID)
df3.show()

df4=df3.join(df2, df3.PatientID == df2.PatientID).drop(df2.PatientID)
df4.show()

df_hba1c=df4.withColumn('HasHighHba1c', F.when(df4.avgvaluehba1c > 8, 1).otherwise(0))
df_hba1c.show()
print "Count: ", df_hba1c.count()

df_glucose=df_hba1c.withColumn('glucoseCategory', F.when(df_hba1c.avgvalueglucose > 150, "high")
.when(df_hba1c.avgvalueglucose.between(100, 150),"moderate").otherwise("ok"))
df_glucose.show()

df_retinopathy=df_glucose.withColumn('HasDiabeticRetinopathy', F.when(df_glucose.avgvaluehba1c > 9.5, 1).otherwise(0))
df_retinopathy.show()


df5=df_retinopathy.join(dfgfr, df_retinopathy.PatientID == dfgfr.PatientID).drop(dfgfr.PatientID)
df5.show()

df_kidney=df5.withColumn('HasKidneyDisease', F.when(df5.avgvaluegfr < 20, 1).otherwise(0))
df_kidney.show()

df_HBA1CCategory=df_kidney.withColumn('HBA1CCategory', F.when(df_kidney.avgvaluehba1c < 7.5, "high").when(df_kidney.avgvaluehba1c.between(6.5, 7.5),"moderate").otherwise("ok"))

df_HBA1CCategory.show()

df_final=df_HBA1CCategory.select('PatientID','PatientGender','PatientRace','PatientEthnicity','HasHighHba1c','HasDiabeticRetinopathy'
,'HasKidneyDisease', 'glucoseCategory', 'HBA1CCategory')
df_final.show()

df_final.count()

dynamicframeout0 = DynamicFrame.fromDF(df_final, glueContext, "df_final")


datasink5 = glueContext.write_dynamic_frame.from_catalog(frame = dynamicframeout0, database = "gluedatacatalog", table_name = "source_diabetes_diabetesstudy", transformation_ctx = "datasink5")

datasink = glueContext.write_dynamic_frame.from_options(frame = dynamicframeout0, connection_type = "s3", connection_options = {"path": "s3://<S3 Bucket Name>/"}, format = "csv", transformation_ctx = "datasink")