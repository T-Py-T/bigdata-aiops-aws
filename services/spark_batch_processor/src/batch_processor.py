from pyspark.sql import SparkSession

def main():
    spark = SparkSession.builder.appName("SparkBatchProcessor").getOrCreate()
    s3_bucket = "s3a://{{ S3_BUCKET }}"
    df = spark.read.parquet(s3_bucket)
    df_transformed = df.filter("column IS NOT NULL")
    df_transformed.show()
    spark.stop()

if __name__ == "__main__":
    main()
