from pyspark.sql import SparkSession

from pyspark.sql.functions import (
    col,
    hour,
    dayofweek,
    month,
    avg,
    count,
    round,
    desc,
    when
)

import os


# ============================================================
# 1. START SPARK
# ============================================================

spark = SparkSession.builder \
    .appName("Mumbai Taxi Data Analysis") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


# ============================================================
# 2. LOAD DATA
# ============================================================

file_path = "data/mumbai_taxi_trips.csv"

df = spark.read.csv(
    file_path,
    header=True,
    inferSchema=True
)

print("\n========================================")
print("       MUMBAI TAXI DATA ANALYSIS")
print("========================================")


# ============================================================
# 3. BASIC STATISTICS
# ============================================================

total_trips = df.count()

avg_distance = df.select(
    round(avg("trip_distance_km"), 2)
).first()[0]

avg_fare = df.select(
    round(avg("fare_amount"), 2)
).first()[0]

avg_passengers = df.select(
    round(avg("passenger_count"), 2)
).first()[0]


print("\n===== BASIC STATISTICS =====")

print("Total Trips:", total_trips)

print("Average Distance (km):",
      avg_distance)

print("Average Fare:",
      avg_fare)

print("Average Passengers:",
      avg_passengers)


# ============================================================
# 4. CREATE TIME COLUMNS
# ============================================================

df = df.withColumn(
    "pickup_hour",
    hour("pickup_datetime")
)

df = df.withColumn(
    "pickup_month",
    month("pickup_datetime")
)

df = df.withColumn(
    "pickup_day",
    dayofweek("pickup_datetime")
)


# ============================================================
# 5. TRIPS BY HOUR
# ============================================================

hourly_trips = df.groupBy(
    "pickup_hour"
).agg(
    count("*").alias("total_trips")
).orderBy(
    "pickup_hour"
)


print("\n===== TRIPS BY HOUR =====")

hourly_trips.show(24)


# ============================================================
# 6. TOP PICKUP LOCATIONS
# ============================================================

top_pickup = df.groupBy(
    "pickup_location"
).agg(
    count("*").alias("total_trips")
).orderBy(
    desc("total_trips")
)


print("\n===== TOP PICKUP LOCATIONS =====")

top_pickup.show(10)


# ============================================================
# 7. TOP DROP-OFF LOCATIONS
# ============================================================

top_dropoff = df.groupBy(
    "dropoff_location"
).agg(
    count("*").alias("total_trips")
).orderBy(
    desc("total_trips")
)


print("\n===== TOP DROP-OFF LOCATIONS =====")

top_dropoff.show(10)


# ============================================================
# 8. MONTHLY TRIPS
# ============================================================

monthly_trips = df.groupBy(
    "pickup_month"
).agg(
    count("*").alias("total_trips")
).orderBy(
    "pickup_month"
)


print("\n===== MONTHLY TRIPS =====")

monthly_trips.show(12)


# ============================================================
# 9. PAYMENT METHOD ANALYSIS
# ============================================================

payment_analysis = df.groupBy(
    "payment_method"
).agg(
    count("*").alias("total_trips"),

    round(
        avg("fare_amount"),
        2
    ).alias("average_fare")

).orderBy(
    desc("total_trips")
)


print("\n===== PAYMENT METHOD ANALYSIS =====")

payment_analysis.show()


# ============================================================
# 10. PASSENGER COUNT ANALYSIS
# ============================================================

passenger_analysis = df.groupBy(
    "passenger_count"
).agg(

    count("*").alias("total_trips"),

    round(
        avg("fare_amount"),
        2
    ).alias("average_fare")

).orderBy(
    "passenger_count"
)


print("\n===== PASSENGER ANALYSIS =====")

passenger_analysis.show()


# ============================================================
# 11. DISTANCE ANALYSIS
# ============================================================

distance_analysis = df.select(

    round(
        avg("trip_distance_km"),
        2
    ).alias("average_distance"),

    round(
        avg(
            when(
                col("trip_distance_km") <= 5,
                col("fare_amount")
            )
        ),
        2
    ).alias("avg_fare_short_trips"),

    round(
        avg(
            when(
                (col("trip_distance_km") > 5) &
                (col("trip_distance_km") <= 15),
                col("fare_amount")
            )
        ),
        2
    ).alias("avg_fare_medium_trips"),

    round(
        avg(
            when(
                col("trip_distance_km") > 15,
                col("fare_amount")
            )
        ),
        2
    ).alias("avg_fare_long_trips")

)


print("\n===== DISTANCE ANALYSIS =====")

distance_analysis.show()


# ============================================================
# 12. LOCATION FARE ANALYSIS
# ============================================================

location_fare = df.groupBy(
    "pickup_location"
).agg(

    count("*").alias("total_trips"),

    round(
        avg("trip_distance_km"),
        2
    ).alias("average_distance"),

    round(
        avg("fare_amount"),
        2
    ).alias("average_fare")

).orderBy(
    desc("total_trips")
)


print("\n===== LOCATION FARE ANALYSIS =====")

location_fare.show(10)


# ============================================================
# 13. SAVE RESULTS
# ============================================================

print("\n===== SAVING RESULTS =====")


# Create results folder

os.makedirs(
    "results",
    exist_ok=True
)


# Spark DataFrame → Pandas → CSV

hourly_trips.toPandas().to_csv(
    "results/trips_by_hour.csv",
    index=False
)


top_pickup.toPandas().to_csv(
    "results/top_pickup_locations.csv",
    index=False
)


top_dropoff.toPandas().to_csv(
    "results/top_dropoff_locations.csv",
    index=False
)


monthly_trips.toPandas().to_csv(
    "results/monthly_trips.csv",
    index=False
)


payment_analysis.toPandas().to_csv(
    "results/payment_analysis.csv",
    index=False
)


passenger_analysis.toPandas().to_csv(
    "results/passenger_analysis.csv",
    index=False
)


distance_analysis.toPandas().to_csv(
    "results/distance_analysis.csv",
    index=False
)


location_fare.toPandas().to_csv(
    "results/location_fare.csv",
    index=False
)


print("\n========================================")
print("Analysis completed successfully!")
print("All results saved in results folder.")
print("========================================")


spark.stop()