import sys
import logging
import rds_config
import pymysql
import random
import datetime
#rds settings
rds_host  = "mysqldb.cbcjkqqxy4dt.us-east-1.rds.amazonaws.com"
name = rds_config.db_username
password = rds_config.db_password
db_name = rds_config.db_name



logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=90)
except:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")
def handler(event, context):
    """
    This function fetches content from mysql RDS instance
    """

    item_count = 0
    patid = random.randint(80,100)
   
    with conn.cursor() as cur:
        rndlabvalue  = random.uniform(98.0,140.0)
        dt = datetime.datetime.now()
        cur.execute('insert into diabetes.Labs  values(3001, "Glucose",'+str(patid)+','+ str(rndlabvalue) +',"' + str(dt) +'")')
        rndlabvalue  = random.uniform(98.0,140.0)
        dt = datetime.datetime.now()
        cur.execute('insert into diabetes.Labs  values(3001, "Glucose",'+str(patid)+','+ str(rndlabvalue) +',"' + str(dt) +'")')
        rndlabvalue  = random.uniform(98.0,140.0)
        dt = datetime.datetime.now()
        cur.execute('insert into diabetes.Labs  values(3001, "Glucose",'+str(patid)+','+ str(rndlabvalue) +',"' + str(dt) +'")')
        conn.commit()
       

    return "Added %d items from RDS MySQL table" %(item_count)