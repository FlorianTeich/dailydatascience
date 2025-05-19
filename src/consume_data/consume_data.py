from confluent_kafka import Consumer, KafkaException, KafkaError
import psycopg2
import json


# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'kafka:9092',  # Kafka broker address
    'group.id': 'my_consumer_group',        # Consumer group ID
    'auto.offset.reset': 'earliest'         # Start reading at the earliest message
}

# Kafka topic to consume from
kafka_topic = 'postgres.public.mytable'  # Replace with the actual topic name if different

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="postgres",
    host="dwh",
    port="5432"
)
cursor = conn.cursor()

# Create the table if it doesn't exist
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mytable2 (
        id SERIAL PRIMARY KEY,
        sepal_length FLOAT,
        sepal_width FLOAT,
        petal_length FLOAT,
        petal_width FLOAT,
        target INT
    )
    """)
    conn.commit()
    print("Table 'mytable2' created or already exists in the 'dwh' database.")
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
                    cursor.execute("""
                        INSERT INTO mytable2 (sepal_length, sepal_width, petal_length, petal_width, target)
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