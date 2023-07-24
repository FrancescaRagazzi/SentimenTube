FROM openjdk:8-jre

ENV PATH $SPARK_DIR/bin:$PATH
ENV SPARK_VERSION=3.4.1
ENV SPARK_DIR=/opt/spark
ENV PATH $SPARK_DIR/bin:$PATH
ADD src/setup/spark-${SPARK_VERSION}-bin-hadoop3/ /opt/spark 
RUN apt-get update && apt-get -y install bash python3 python3-pip netcat procps
ENV PATH $PATH:/usr/local/bin/python3
RUN pip3 install pyspark==${SPARK_VERSION} numpy "elasticsearch==8.2.0" pandas nltk pyarrow
ENV PYSPARK_PYTHON=/usr/bin/python3
RUN export PYSPARK_PYTHON=/usr/local/bin/python3

ADD src/code/*  /opt/tap/
ADD src/spark-manager.sh $SPARK_DIR/bin/spark-manager

RUN chmod +x $SPARK_DIR/bin/spark-manager

WORKDIR ${SPARK_DIR}
ENTRYPOINT [ "spark-manager", "sentiment_spark.py", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,com.johnsnowlabs.nlp:spark-nlp_2.12:5.0.0,org.elasticsearch:elasticsearch-spark-30_2.12:8.2.0" ]