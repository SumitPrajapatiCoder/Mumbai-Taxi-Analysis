from pyspark.sql import SparkSession
from pyspark.sql.functions import col


spark = SparkSession.builder \
    .appName("Mumbai Taxi Data Cleaning") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")
file_path = "data/mumbai_taxi_trips.csv"

df = spark.read.csv(
    file_path,
    header=True,
    inferSchema=True
)

print("\n===== ORIGINAL DATA =====")
print("Rows:", df.count())
print("Columns:", len(df.columns))


print("\n===== MISSING VALUES =====")

for column in df.columns:
    count = df.filter(col(column).isNull()).count()
    print(column, ":", count)


print("\n===== DUPLICATE TRIPS =====")

duplicate_count = df.count() - df.dropDuplicates(["trip_id"]).count()

print("Duplicate trip IDs:", duplicate_count)


print("\n===== INVALID VALUES =====")

invalid_passengers = df.filter(
    (col("passenger_count") <= 0) |
    (col("passenger_count") > 6)
).count()

invalid_distance = df.filter(
    (col("trip_distance_km") <= 0)
).count()

invalid_fare = df.filter(
    (col("fare_amount") <= 0)
).count()

print("Invalid passenger counts:", invalid_passengers)
print("Invalid distances:", invalid_distance)
print("Invalid fares:", invalid_fare)


clean_df = df.dropDuplicates(["trip_id"])

clean_df = clean_df.filter(
    (col("passenger_count") > 0) &
    (col("passenger_count") <= 6) &
    (col("trip_distance_km") > 0) &
    (col("fare_amount") > 0)
)


print("\n===== CLEAN DATA =====")

print("Original rows:", df.count())
print("Clean rows:", clean_df.count())
print("Removed rows:", df.count() - clean_df.count())

print("\n===== CLEAN DATA SAMPLE =====")

clean_df.show(10, truncate=False)

spark.stop()