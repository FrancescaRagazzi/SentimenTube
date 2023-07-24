from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf
from pyspark.sql.types import ArrayType, StringType, StructField, StructType, FloatType
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from elasticsearch import Elasticsearch

nltk.download('vader_lexicon') 

kafka_server = "10.0.100.23:9092"
elasticsearch_host = "http://10.0.100.27"
elasticsearch_port = "9200"
elasticsearch_index = "sentiment_analysis"

def write_to_elasticsearch(df):
    es = Elasticsearch(f"{elasticsearch_host}:{elasticsearch_port}", verify_certs=False)
    df.write \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", elasticsearch_index) \
        .option("es.nodes", elasticsearch_host) \
        .option("es.port", elasticsearch_port) \
        .option("es.index.auto.create", "true") \
        .mode("append") \
        .save()

def calculate_sentiment_score(comment):
    if comment:
        scores = [sia.polarity_scores(c)["compound"] for c in comment]
        return sum(scores) / len(scores) if scores else None
    else:
        return None

def calculate_comment_sentiment(comment):
    if comment:
        sentiment_scores = [sia.polarity_scores(c)["compound"] for c in comment]
        return sentiment_scores
    else:
        return None

spark = SparkSession.builder \
    .appName("SentimentAnalysis") \
    .getOrCreate()

schema = StructType([
    StructField("comments", ArrayType(StringType()), nullable=True),
    StructField("title", StringType(), nullable=True),
    StructField("@timestamp", StringType(), nullable=True),
    StructField("channel_title", StringType(), nullable=True),
    StructField("like_count", FloatType(), nullable=True),
    StructField("@version", StringType(), nullable=True),
    StructField("video_id", StringType(), nullable=True),
    StructField("view_count", FloatType(), nullable=True),
    StructField("comment_count", FloatType(), nullable=True),
    StructField("dislike_count", FloatType(), nullable=True)
])

sia = SentimentIntensityAnalyzer()

# registra UDF
calculate_sentiment_score_udf = udf(calculate_sentiment_score, FloatType())
calculate_comment_sentiment_udf = udf(calculate_comment_sentiment, ArrayType(FloatType()))

# legge da kafka
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_server) \
    .option("subscribe", "videos") \
    .load()

# decodicfica json 
parsed_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")) \
    .select("data.*")


sentiment_df = parsed_df.withColumn("sentiment_score", calculate_sentiment_score_udf(col("comments")))
comment_sentiment_df = sentiment_df.withColumn("comment_sentiment", calculate_comment_sentiment_udf(col("comments")))

output_df = comment_sentiment_df.select("comments", "title", "@timestamp", "channel_title", "like_count",
                                        "@version", "video_id", "view_count", "comment_count", "dislike_count",
                                        "sentiment_score", "comment_sentiment")


output_df.writeStream \
    .outputMode("update") \
    .foreachBatch(lambda df, epochId: write_to_elasticsearch(df)) \
    .start() \
    .awaitTermination()
