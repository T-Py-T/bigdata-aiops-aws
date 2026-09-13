FROM spark:4.2.0-python3@sha256:be7657ac5f672782b8301866cf5efe0cff5d688a1a2e28748447d326d6d8aa28
WORKDIR /opt/spark/work-dir/app
COPY --chown=spark:spark src/ .
CMD ["/opt/spark/bin/spark-submit", "realtime_processor.py"]
