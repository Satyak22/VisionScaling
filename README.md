# VisionScaling

The project shows a pipeline for recognizing images in real time. It simulates message streaming using Kafka and classifies image in real time.

### Cluster Setup Instructions

There are 4 nodes in the cluster where one node acts as a Producer and the rest 3 acts as a Consumer.

The following things are need to be installed on each of the nodes in the cluster.

1) Java 8
2) Confluent Kafka - here
3) Python library for confluent kafka
4) Pytorch for executing Deep Learning model
5) Faust for stream processing on Consumer Nodes
6) psycopg2 - Python library for interacting with PostgreSQL database
7) boto3 - Python library for interacting with AWS EC2 and S3.

### Database Instructions

PostgreSQL is used for storing the image keys for each image in S3. Image keys here refer to the string which is used to access the image files from S3. Also, the results from the Deep Learning model are stored in PostgreSQL.

There is one database called my_db and there are two tables in the database.

1) image_info

| image_key |
|-----------|

2) prediction_results

| image_key | category | confidence | hostname | time |
|-----------|----------|------------|----------|------|


### Introduction

##### What exactly does this project do?
This project simulates the streaming application. It fetches image keys from PostgreSQL, passes them as stream through Kafka cluster which further downloads images from S3, runs the inference using SqueezeNet model and writes the output back into PostgreSQL.

There are images stored in S3 and their corresponding image_keys in PostgreSQL. This was achieved through upload.py script. The Producer will fetch those image keys from PostgreSQL and publish them to Kafka topic across 3 partitions. The Consumer nodes will fetch those image keys from those partitions, downloads the image keys from S3, runs the inference using SqueezeNet model and writes the result to PostgreSQL.


##### Where does this project prove useful?
For companies having their warehouses store and organize their products, this pipeline helps in the automation of that process.

![Robot](images/usecase.png | width=100)

As seen in the above picture, that the robot is trying to organize the objects based on color. Similarly, using the images, this pipeline helps in organizing the objects into different bins based on the category it belongs to. For eg, in a manufacturing industry, organizing parts of the machine based on its type. Is it a general purpose part?, Is it specific to machine A? and so on. In a warehouse, there are multiple such belts that are carrying objects which creates the need for producing results within seconds or even less.


##### How would this work in a real world scenario?
For the real world applications, the incoming images will be stored in S3 and their respective image keys will directly be streamed to Kafka topic. The rest of the pipeline remains the same which includes downloading, running the prediction model and writing the output to the database. The difference will be that the image keys will not be stored in PostgreSQl and directly streamed to Kafka cluster.


### Architecture


### Dataset
