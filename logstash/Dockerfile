FROM docker.elastic.co/logstash/logstash:8.8.2
RUN logstash-plugin install logstash-output-http
ADD pipeline/* /usr/share/logstash/pipeline/ 
