from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("RealtimeProcessor").getOrCreate()
    try:
        s3_bucket = "s3a://{{ S3_BUCKET }}"
        df = spark.readStream.format("parquet").load(s3_bucket)
        query = df.writeStream.format("console").start()
        query.awaitTermination()
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
