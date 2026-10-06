from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("Mumbai Taxi Data Analysis") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

file_path = "data/mumbai_taxi_trips.csv"

# Load CSV
df = spark.read.csv(
    file_path,
    header=True,
    inferSchema=True
)

# Display first 10 rows
print("\n===== SAMPLE DATA =====")
df.show(10, truncate=False)

# Display column names
print("\n===== COLUMNS =====")
print(df.columns)

# Display number of rows
print("\n===== NUMBER OF ROWS =====")
print(df.count())

# Display data types
print("\n===== DATA TYPES =====")
df.printSchema()

spark.stop()