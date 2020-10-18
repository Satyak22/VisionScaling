import faust
import psycopg2

app = faust.App('image_files', broker='kafka://10.0.0.8:9092', value_serializer='raw')

db_topic = app.topic('postgres')

# Establishing connection to PostgreSQL database.
def get_connection():
	connection = psycopg2.connect(user = "db_select",
	                              password = "test123",
	                              host = '10.0.0.11',
	                              port = "5431",
	                              database = "my_db")

	connection.autocommit = True

	return connection


# Agent that subscribes to db_topic and handles the insert queries into database.
@app.agent(db_topic)
async def store_results(records):
	connection = get_connection()
	cursor = connection.cursor()

	async for record in records:
		cursor.execute("insert into prediction_results values(" + record.decode('utf-8') + ");")
		print("Record Inserted")
