import faust
import torch
from torchvision import models, transforms
from PIL import Image
import json
import os
import boto3
import psycopg2
import socket
from datetime import datetime
from confluent_kafka import Producer

app = faust.App('image_files', broker='kafka://10.0.0.8:9092', value_serializer='raw')

my_topic = app.topic('img_loc')


# Producer Callback
def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {0}: {1}"
              .format(msg.value(), err.str()))
    else:
        print("Message produced: {0}".format(msg.value()))

# Computes inference for image and determines category.
def inference(sq_net, transform, classes, filepath, s3, p):
	hostname = socket.gethostname()

	# downloading images based on image keys
	s3.download_file('imagenet-files', filepath, filepath)

	# Reading image and applying defined transformation
	img = Image.open(filepath).convert('RGB')
	img_t = transform(img)
	batch_t = torch.unsqueeze(img_t,0)

	# Predicting the label for input image
	sq_net.eval()
	out = sq_net(batch_t)

	# Using Softmax layer, getting the confidence and finding category with max confidence.
	confidence = torch.nn.functional.softmax(out, dim=1)[0]*100
	_,idx = torch.max(out, 1)

	print("Done processing file: ", filepath)

	category, confidence = classes[idx[0]], confidence[idx[0]].item()
	current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	# Creating query string for inserting into database and producing to kafka topic.
	query_str = "'" + filepath + "','" + category + "'," + str(confidence) + "," + str(app.monitor.messages_s) + ",'" + hostname + "','" + current_timestamp + "'"
	p.produce('postgres', query_str, callback=acked)

	# Removing the downloaded file after it has been processed to avoid occupying disk space.
	os.remove(filepath)

# Creating Labels array
def create_labels_array():

  file = open("Classes.txt")
  classes = []
  for line in file.readlines():
    classes.append(line.split(":")[1].strip()[:-1])
  
  return classes


# Agent that subscribes to my_topic which handles the inferences using SqueezeNet model.
@app.agent(my_topic, concurrency=10)
async def display_image_files(records):

	# Load pre trained squeezenet model
	sq_net = models.squeezenet1_1(pretrained=True, progress=True)

	# Image Transformation Specifications
	transform = transforms.Compose([
	                        transforms.Resize(256),
	                        transforms.CenterCrop(224),
	                        transforms.ToTensor(),
	                        transforms.Normalize(
	                            mean=[0.485, 0.456, 0.406],
	                            std=[0.229, 0.224, 0.225]
	                        )])

	s3 = boto3.client('s3', region_name='us-west-2')

	p = Producer({'bootstrap.servers': '10.0.0.8:9092'})

	# Loading dictionary with labels for their corresponding index.
	classes = create_labels_array()

	async for record in records:
		inference(sq_net, transform, classes, record.decode('utf-8'), s3, p)
