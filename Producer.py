import psycopg2
import boto3
import time
from confluent_kafka import Producer

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: {0}: {1}"
              .format(msg.value(), err.str()))
    else:
        print("Message produced: {0}".format(msg.value()))


def get_postgre_dns():
	ec2 = boto3.client('ec2', region_name='us-west-2')
	response = ec2.describe_instances()

	num_instances = len(response['Reservations'])
	public_dns = ""

	for x in range(num_instances):
		if response['Reservations'][x]['Instances'][0]['Tags'][0]['Value'] == "Postgres":
			public_dns = response['Reservations'][x]['Instances'][0]['PublicDnsName']
			break

	return public_dns

def get_connection(public_dns):
	connection = psycopg2.connect(user = "db_select",
	                              password = "test123",
	                              host = public_dns,
	                              port = "5431",
	                              database = "my_db")

	connection.autocommit = True

	return connection


def main():

	try:

		public_dns = get_postgre_dns()
		connection = get_connection(public_dns)

		cursor = connection.cursor()

		cursor.execute("select image_key from image_info fetch first 100 rows only;")

		p = Producer({'bootstrap.servers': '10.0.0.8:9092'})

		while True:
			records = cursor.fetchmany(20)

			if not records:
				break

			for row in records:
				p.produce('img_loc', row[0], callback=acked)
				p.poll(0.5)

	except (Exception, psycopg2.Error) as error:
		print(error)


main()