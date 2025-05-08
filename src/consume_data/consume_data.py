from confluent_kafka import Consumer, KafkaException, KafkaError

# Kafka configuration
kafka_config = {
    'bootstrap.servers': 'kafka:9092',  # Kafka broker address
    'group.id': 'my_consumer_group',        # Consumer group ID
    'auto.offset.reset': 'earliest'         # Start reading at the earliest message
}

# Kafka topic to consume from
kafka_topic = 'postgres.public.mytable'  # Replace with the actual topic name if different

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
                print(f"Received message: {msg.value().decode('utf-8')}")

    except KeyboardInterrupt:
        print("Consumer interrupted by user")
    finally:
        # Close the consumer
        consumer.close()

if __name__ == "__main__":
    consume_changes()