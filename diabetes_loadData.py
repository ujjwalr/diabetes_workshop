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



datasource1 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_hba1c", transformation_ctx = "datasource1")



datasource2 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_glucose", transformation_ctx = "datasource2")


datasource3 = glueContext.create_dynamic_frame.from_catalog(database = "gluedatacatalog", table_name = "source_diabetes_gfr"
, transformation_ctx = "datasource3")



df4=df0.join(df1, df0.PatientID == df1.PatientID).drop(df1.PatientID).drop(df1.Labtype)


df5=df4.join(df2, df4.PatientID == df2.PatientID).drop(df2.PatientID).drop(df2.Labtype)


df6=df5.join(df3, df5.PatientID == df3.PatientID).drop(df3.PatientID).drop(df3.Labtype)



df_hba1c=df6.withColumn('hasHighHba1c', F.when(df6.avgvaluehba1c < 6, 0).otherwise(1))




df_glucose=df_hba1c.withColumn('glucoseCategory', F.when(df_hba1c.avgvalueglucose < 70, "low").when(df_hba1c.avgvalueglucose.between(70, 100),"ok").when(df_hba1c.avgvalueglucose.between(101, 130),"high").otherwise("very high"))



df_gfr=df_glucose.withColumn('HasKidneyDisease', F.when(df_glucose.avgvaluegfr < 20, 0).otherwise(1))




df_final=df_gfr.select('PatientID','PatientGender','PatientRace','PatientEthnicity','hasHighHba1c','glucoseCategory','HasKidneyDisease')


dynamicframeout0 = DynamicFrame.fromDF(df_final, glueContext, "df_final")

datasink5 = glueContext.write_dynamic_frame.from_catalog(frame = dynamicframeout0, database = "gluedatacatalog", table_name = "source_diabetes_diabetesstudy", transformation_ctx = "datasink5")


datasink6 = glueContext.write_dynamic_frame.from_options(frame = dynamicframeout0,  connection_type = "s3", connection_options = {"path": "s3://diabetesdata/diabetesworkshop/"}, format = "csv", transformation_ctx = "datasink6")