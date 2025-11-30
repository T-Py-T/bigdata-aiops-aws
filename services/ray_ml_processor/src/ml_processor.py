# services/ray_ml_processor/src/ml_processor.py
# Bridges Kafka message streams to Ray distributed ML processing
# Handles: actor-based inference, batch processing, Kafka consume/produce, Ray initialization

import os
import json
import logging
from typing import Dict, Any, List
import ray
from ray import serve
from kafka import KafkaConsumer, KafkaProducer
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@ray.remote
class MLModelActor:
    """Ray actor for ML model inference"""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
        logger.info(f"Initializing ML Model Actor: {model_name}")
        # Initialize your ML model here
        # Example: self.model = joblib.load(f'models/{model_name}.pkl')
        self.inference_count = 0
        
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on input features"""
        self.inference_count += 1
        logger.info(f"Running inference #{self.inference_count} with model {self.model_name}")
        
        # Example ML processing - replace with your actual model
        result = {
            "model": self.model_name,
            "prediction": "example_prediction",
            "confidence": 0.95,
            "features": features,
            "inference_id": self.inference_count
        }
        
        return result
    
    def batch_predict(self, features_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run batch inference"""
        logger.info(f"Running batch inference on {len(features_batch)} samples")
        return [self.predict(features) for features in features_batch]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        return {
            "model_name": self.model_name,
            "total_inferences": self.inference_count
        }


@ray.remote
def process_data_task(data: Dict[str, Any]) -> Dict[str, Any]:
    """Stateless data processing task"""
    logger.info(f"Processing data task: {data.get('id', 'unknown')}")
    
    # Example data transformation
    processed = {
        "original": data,
        "processed": True,
        "features_extracted": {
            "feature_1": np.random.random(),
            "feature_2": np.random.random(),
        }
    }
    
    return processed


class KafkaRayBridge:
    """Bridge between Kafka and Ray for ML processing"""
    
    def __init__(self):
        self.kafka_broker = os.getenv('KAFKA_BROKER', 'kafka-service:9092')
        self.input_topic = os.getenv('INPUT_TOPIC', 'ml_input')
        self.output_topic = os.getenv('OUTPUT_TOPIC', 'ml_output')
        self.ray_address = os.getenv('RAY_ADDRESS', 'auto')
        
        logger.info(f"Initializing Kafka-Ray Bridge")
        logger.info(f"Kafka Broker: {self.kafka_broker}")
        logger.info(f"Input Topic: {self.input_topic}")
        logger.info(f"Output Topic: {self.output_topic}")
        logger.info(f"Ray Address: {self.ray_address}")
        
        # Initialize Ray
        if not ray.is_initialized():
            ray.init(address=self.ray_address, namespace="ml-processing")
        
        # Create ML model actors
        self.num_models = int(os.getenv('NUM_MODELS', '3'))
        self.models = [
            MLModelActor.remote(f"model_{i}") 
            for i in range(self.num_models)
        ]
        logger.info(f"Created {self.num_models} ML model actors")
        
        # Initialize Kafka consumer and producer
        self.consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=[self.kafka_broker],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='ray-ml-processor'
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=[self.kafka_broker],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
    def process_messages(self):
        """Main processing loop"""
        logger.info("Starting message processing loop...")
        batch_size = int(os.getenv('BATCH_SIZE', '10'))
        batch = []
        
        try:
            for message in self.consumer:
                data = message.value
                logger.info(f"Received message: {data.get('id', 'unknown')}")
                
                batch.append(data)
                
                # Process in batches
                if len(batch) >= batch_size:
                    self._process_batch(batch)
                    batch = []
                    
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if batch:
                self._process_batch(batch)
        finally:
            self.consumer.close()
            self.producer.close()
    
    def _process_batch(self, batch: List[Dict[str, Any]]):
        """Process a batch of messages using Ray"""
        logger.info(f"Processing batch of {len(batch)} messages")
        
        # Distribute work across Ray actors
        futures = []
        for i, data in enumerate(batch):
            model_idx = i % self.num_models
            future = self.models[model_idx].predict.remote(data)
            futures.append(future)
        
        # Collect results
        results = ray.get(futures)
        
        # Send results to output topic
        for result in results:
            self.producer.send(self.output_topic, value=result)
            logger.info(f"Sent result to {self.output_topic}")
        
        self.producer.flush()
        logger.info(f"Completed batch processing")


@serve.deployment(num_replicas=1)
class MLServeDeployment:
    """Ray Serve deployment for HTTP endpoint"""
    
    def __init__(self):
        self.model = MLModelActor.remote("serve_model")
        
    async def __call__(self, request):
        data = await request.json()
        result = await self.model.predict.remote(data)
        return result


def main():
    """Main entry point"""
    mode = os.getenv('MODE', 'kafka')
    
    if mode == 'kafka':
        logger.info("Starting in Kafka mode")
        bridge = KafkaRayBridge()
        bridge.process_messages()
    elif mode == 'serve':
        logger.info("Starting in Ray Serve mode")
        serve.run(MLServeDeployment.bind(), host="0.0.0.0", port=8000)
    else:
        logger.error(f"Unknown mode: {mode}")


if __name__ == "__main__":
    main()

