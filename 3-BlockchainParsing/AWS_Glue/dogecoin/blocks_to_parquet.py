import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
## @type: DataSource
## @args: [database = "ethereumetl", table_name = "blocks", transformation_ctx = "data_source"]
## @return: data_source
## @inputs: []
data_source = glueContext.create_dynamic_frame.from_catalog(database="dogecoin", table_name="blocks_csv",
                                                            transformation_ctx="data_source")
## @type: ApplyMapping
## @args: [mapping = [("block_number", "long", "block_number", "long"), ("block_hash", "string", "block_hash", "string"), ("block_parent_hash", "string", "block_parent_hash", "string"), ("block_nonce", "string", "block_nonce", "string"), ("block_sha3_uncles", "string", "block_sha3_uncles", "string"), ("block_logs_bloom", "string", "block_logs_bloom", "string"), ("block_transactions_root", "string", "block_transactions_root", "string"), ("block_state_root", "string", "block_state_root", "string"), ("block_miner", "string", "block_miner", "string"), ("block_difficulty", "long", "block_difficulty", "long"), ("block_total_difficulty", "long", "block_total_difficulty", "long"), ("block_size", "long", "block_size", "long"), ("block_extra_data", "string", "block_extra_data", "string"), ("block_gas_limit", "long", "block_gas_limit", "long"), ("block_gas_used", "long", "block_gas_used", "long"), ("block_timestamp", "long", "block_timestamp", "long"), ("block_transaction_count", "long", "block_transaction_count", "long")], transformation_ctx = "applymapping1"]
## @return: mapped_frame
## @inputs: [frame = data_source]
mapped_frame = ApplyMapping.apply(frame=data_source, mappings=[
    ("height", "long", "height", "long"),
    ("hash", "string", "hash", "string"),
    ("n_tx", "long", "n_tx", "long"),
    ("tx", "string", "block_hash", "string"),
    ("time", "long", "time", "long")],
                                  transformation_ctx="mapped_frame")

## @type: ResolveChoice
## @args: [choice = "make_struct", transformation_ctx = "resolve_choice_frame"]
## @return: resolve_choice_frame
## @inputs: [frame = mapped_frame]
resolve_choice_frame = ResolveChoice.apply(frame=mapped_frame, choice="make_struct",
                                           transformation_ctx="resolve_choice_frame")
## @type: DropNullFields
## @args: [transformation_ctx = "drop_null_fields_frame"]
## @return: drop_null_fields_frame
## @inputs: [frame = resolve_choice_frame]
drop_null_fields_frame = DropNullFields.apply(frame=resolve_choice_frame, transformation_ctx="drop_null_fields_frame")
## @type: DataSink
## @args: [connection_type = "s3", connection_options = {"path": "s3://<your_bucket>/ethereumetl/parquet/blocks"}, format = "parquet", transformation_ctx = "data_sink"]
## @return: data_sink
## @inputs: [frame = drop_null_fields_frame]
data_sink = glueContext.write_dynamic_frame.from_options(frame=drop_null_fields_frame,
                                                         connection_type="s3",
                                                         connection_options={
                                                             "path": "s3://ethereumxxx/dogecoin/blocks"},
                                                         format="parquet", transformation_ctx="data_sink")
job.commit()