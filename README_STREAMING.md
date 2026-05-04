# Spark Streaming Homework - Complete Guide

## Overview
This solution includes:
1. **Spark_Streaming_Homework.ipynb** - Main Jupyter notebook with all tasks
2. **weather_api_producer.py** - External Python script for weather API polling

## Prerequisites
- Apache Spark installed with PySpark
- Python 3.7+
- Required packages: requests, pandas
- Jupyter Notebook

## Installation

### Install Required Packages
```bash
pip install pyspark requests
```

### Configure Paths
Update the following paths in the notebook and script if needed:
- BASE_DIR: Path to Spark for DQE directory
- Input data folder location
- Output data folder location

## Running the Solution

### Step 1: Start Jupyter Notebook
```bash
jupyter notebook
```

### Step 2: Open and Run the Main Notebook
1. Open `Spark_Streaming_Homework.ipynb`
2. Run all cells in sequence
3. The notebook will:
   - Load sales.csv and verify > 4M records
   - Create seller_id=7 dataframe
   - Set up CSV streaming pipeline with 10-second micro-batch
   - Set up weather streaming pipeline with 30-minute trigger
   - Create memory sink for weather aggregations
   - Display processed data from output folders

### Step 3: Run Weather API Producer (Optional, in separate terminal)
```bash
python weather_api_producer.py
```

This script will:
- Start polling the open-meteo weather API every 30 seconds (production: 30 minutes)
- Write JSON files to `user_weather/` folder
- Spark streaming will automatically detect and process these files

## Task Breakdown

### Task 1: CSV Streaming Pipeline
✓ **1.1** - Load sales.csv into static DataFrame
✓ **1.2** - Verify count > 4 million records
✓ **1.3** - Create separate DataFrame for seller_id = 7
✓ **1.4** - Create input_data folder and streaming source
✓ **1.5** - Configure CSV sink with date partitioning and 10s trigger
✓ **1.6** - Write seller_7 data to input_data folder
✓ **1.7** - Inspect processed output files in output_data folder

**Output Structure:**
```
output_data/
  date=2000-01-01/
    part-00000.csv
    part-00001.csv
  date=2000-01-02/
    part-00000.csv
  ...
```

### Task 2: Weather Streaming Pipeline
✓ **2.1** - Create streaming source from JSON files with specified schema
✓ **2.2** - Calculate average temperature of streaming data
✓ **2.3** - Configure memory sink with 30-minute trigger
✓ **2.4** - Create weather API producer script (weather_api_producer.py)
✓ **2.5** - Query in-memory table via SQL

**Memory Table Query:**
```python
spark.sql("SELECT * FROM weather_avg_temperature").show()
```

### Task 3 (Optional): Kafka Streaming Pipeline
✓ **3.1** - Create Kafka cluster using Aiven OR local Docker
✓ **3.2** - Create Kafka topic (`topic-for-spark`)
✓ **3.3** - Create Spark session with Kafka package
✓ **3.4** - Create Kafka output sink for streaming DataFrame
✓ **3.5** - Write Task 1 static DataFrame (`seller_id = 7`) to `input_data`
✓ **3.6** - Pull and verify messages from Kafka topic

Run implementation script:
```bash
python task3_kafka_streaming.py
```

#### Option A: Aiven Kafka
Set environment variables before running script:

Windows PowerShell:
```powershell
$env:KAFKA_BOOTSTRAP_SERVERS = "<aiven-host>:<port>"
$env:KAFKA_TOPIC = "topic-for-spark"
$env:KAFKA_SECURITY_PROTOCOL = "SASL_SSL"
$env:KAFKA_SASL_MECHANISM = "PLAIN"
$env:KAFKA_USERNAME = "<aiven-service-username>"
$env:KAFKA_PASSWORD = "<aiven-service-password>"
python task3_kafka_streaming.py
```

#### Option B: Local Docker Kafka
Start local Kafka and run script:
```bash
docker compose -f docker-compose.kafka.yml up -d
python task3_kafka_streaming.py
```

## File Structure
```
dqe-automation/
├── Spark_Streaming_Homework.ipynb
├── weather_api_producer.py
├── README_STREAMING.md (this file)
├── input_data/           (created by notebook)
├── output_data/          (created by notebook)
├── user_weather/         (created by notebook)
└── checkpoints/          (created by notebook)
```

## Configuration Details

### Spark Session Settings
- AppName: Spark_Streaming_Homework
- Streaming checkpoint location: checkpoints folder

### CSV Streaming Source
- Source: input_data folder
- Format: CSV with headers
- Deduplication: By order_id column
- Checkpoint: checkpoints/csv_sink

### CSV Streaming Sink
- Output: output_data folder
- Format: CSV with headers
- Partitioning: By date column
- Trigger: 10 seconds (micro-batch)
- Checkpoint: checkpoints/csv_sink

### Weather Streaming Source
- Source: user_weather folder
- Format: JSON
- Schema: Includes is_day, temperature, time, weathercode, winddirection, windspeed

### Weather Memory Sink
- Output: In-memory table named "weather_avg_temperature"
- Trigger: 30 minutes (for production)
- Output Mode: Complete
- Checkpoint: checkpoints/weather_memory_sink

## Weather API Producer Details

### Configuration
- Poll Interval: 30 seconds (change to 1800 for production)
- Number of Users: 20
- User Locations: Random coordinates
- API: open-meteo (free, no authentication required)
- Output Format: JSON files

### API Response Format
```json
{
  "latitude": 45.5,
  "longitude": -122.5,
  "generationtime_ms": 0.5,
  "utc_offset_seconds": -25200,
  "timezone": "America/Los_Angeles",
  "timezone_abbreviation": "PDT",
  "elevation": 100,
  "current_weather": {
    "temperature": 20.5,
    "windspeed": 10.2,
    "winddirection": 180,
    "weathercode": 0,
    "time": "2024-01-01T12:00",
    "is_day": 1
  }
}
```

### File Naming Convention
`user_weather/[user_id]_[timestamp]_weather.json`

Example: `user_weather/user0_20240101_120000_weather.json`

## Monitoring Streams

### Check Active Queries
```python
# In notebook
streaming_query.isActive
weather_memory_query.isActive
```

### View Stream Progress
```python
# CSV stream progress
streaming_query.lastProgress

# Weather stream progress
weather_memory_query.lastProgress
```

### Stop Streams (when done)
```python
streaming_query.stop()
weather_memory_query.stop()
```

## Troubleshooting

### Problem: "Input path does not exist"
- Solution: Make sure input_data folder is created (done in notebook)

### Problem: Stream not processing new files
- Check that files are in the correct folder (input_data)
- Ensure checkpoint directory has write permissions
- Verify data format matches schema

### Problem: Weather API errors
- Check internet connection
- Verify open-meteo API is accessible
- Check rate limiting (add delays if needed)

### Problem: Memory sink not showing data
- Ensure weather JSON files are in user_weather folder
- Check that JSON format matches the defined schema
- Verify memory_query is still active

## Performance Notes
- CSV files should use single coalesce for better performance
- Weather API calls are rate-limited; use delays between requests
- For production, adjust poll interval to 30 minutes (1800 seconds)
- Checkpoint directories consume disk space; clean periodically

## References
- Apache Spark Streaming Docs: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- Open-Meteo API: https://open-meteo.com/
- PySpark Documentation: https://spark.apache.org/docs/latest/api/python/
