from confluent_kafka import Consumer, KafkaException, KafkaError
import psycopg2
import json
import os


# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'kafka:9092',  # Kafka broker address
    'group.id': 'my_consumer_group',        # Consumer group ID
    'auto.offset.reset': 'earliest'         # Start reading at the earliest message
}

# Kafka topic to consume from
kafka_topic = 'postgres.public.iris_original'  # Replace with the actual topic name if different

print('POSTGRES_HOST', os.getenv("POSTGRES_HOST", ""))
print('POSTGRES_PORT', os.getenv("POSTGRES_PORT", ""))
print('POSTGRES_DB', os.getenv("POSTGRES_DB", ""))
print('POSTGRES_USER', os.getenv("POSTGRES_USER", ""))
print('POSTGRES_PASSWORD', os.getenv("POSTGRES_PASSWORD", ""))

conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB", ""),
    user=os.getenv("POSTGRES_USER", ""),
    password=os.getenv("POSTGRES_PASSWORD", ""),
    host=os.getenv("POSTGRES_HOST", ""),
    port=os.getenv("POSTGRES_PORT", "")
)
cursor = conn.cursor()

# Create the table if it doesn't exist
tablename = os.getenv("DATA_TABLE", "")
try:
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {tablename} (
        id SERIAL PRIMARY KEY,
        sepal_length FLOAT,
        sepal_width FLOAT,
        petal_length FLOAT,
        petal_width FLOAT,
        target INT
    )
    """)
    conn.commit()
    print(f"Table {tablename} created or already exists in the 'dwh' database.")
except Exception as e:
    print(f"Failed to create table: {e}")

def consume_changes():
    # Create a Kafka consumer
    consumer = Consumer(kafka_config)

    try:
        # Subscribe to the topic
        consumer.subscribe([kafka_topic])

        print(f"Consuming messages from topic: {kafka_topic}")
        while True:
            # Poll for messages
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue  # No message received, continue polling
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    print(f"Reached end of partition: {msg.topic()} [{msg.partition()}]")
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Successfully received a message
                #print(f"Received message: {msg.value().decode('utf-8')}")

                # Parse the message and insert it into the database
                try:
                    data = json.loads(msg.value().decode('utf-8'))
                    cursor.execute(f"""
                        INSERT INTO {tablename} (sepal_length, sepal_width, petal_length, petal_width, target)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (
                        data['payload']['after']['sepal_length'],
                        data['payload']['after']['sepal_width'],
                        data['payload']['after']['petal_length'],
                        data['payload']['after']['petal_width'],
                        data['payload']['after']['target']
                    ))
                    conn.commit()
                    print()
                    print("Successfully inserted data into database:")
                    print(f"sepal_length: {data['payload']['after']['sepal_length']}")
                    print()
                except Exception as e:
                    print(f"Failed to insert data into database: {e}")

    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    finally:
        # Close the consumer
        consumer.close()

if __name__ == "__main__":
    consume_changes()
