import os
import pandas as pd

from django.conf import settings
from django.shortcuts import render


def dashboard(request):

    # =========================================================
    # 1. DATASET PATH
    # =========================================================

    data_file = os.path.join(
        settings.BASE_DIR,
        "data",
        "mumbai_taxi_trips.csv"
    )

    # =========================================================
    # 2. READ DATASET
    # =========================================================

    df = pd.read_csv(
        data_file,
        usecols=[
            "pickup_location",
            "dropoff_location",
            "pickup_datetime",
            "passenger_count",
            "trip_distance_km",
            "fare_amount",
            "payment_method"
        ]
    )

    # Convert datetime
    df["pickup_datetime"] = pd.to_datetime(
        df["pickup_datetime"]
    )

    # =========================================================
    # 3. GET FILTER VALUES FROM URL
    # =========================================================

    selected_pickup = request.GET.get(
        "pickup_location",
        ""
    )

    selected_payment = request.GET.get(
        "payment_method",
        ""
    )

    selected_passenger = request.GET.get(
        "passenger_count",
        ""
    )

    # =========================================================
    # 4. DROPDOWN OPTIONS
    # =========================================================

    pickup_locations = sorted(
        df["pickup_location"]
        .dropna()
        .unique()
        .tolist()
    )

    payment_methods = sorted(
        df["payment_method"]
        .dropna()
        .unique()
        .tolist()
    )

    passenger_counts = sorted(
        df["passenger_count"]
        .dropna()
        .unique()
        .tolist()
    )

    # =========================================================
    # 5. APPLY FILTERS
    # =========================================================

    filtered_df = df.copy()

    # Pickup Location
    if selected_pickup:
        filtered_df = filtered_df[
            filtered_df["pickup_location"] == selected_pickup
        ]

    # Payment Method
    if selected_payment:
        filtered_df = filtered_df[
            filtered_df["payment_method"] == selected_payment
        ]

    # Passenger Count
    if selected_passenger:
        try:
            passenger_value = int(selected_passenger)

            filtered_df = filtered_df[
                filtered_df["passenger_count"] == passenger_value
            ]

        except ValueError:
            pass

    # =========================================================
    # 6. BASIC STATISTICS / KPI
    # =========================================================

    total_trips = len(filtered_df)

    if total_trips > 0:

        avg_distance = round(
            filtered_df["trip_distance_km"].mean(),
            2
        )

        avg_fare = round(
            filtered_df["fare_amount"].mean(),
            2
        )

        avg_passengers = round(
            filtered_df["passenger_count"].mean(),
            2
        )

    else:

        avg_distance = 0
        avg_fare = 0
        avg_passengers = 0

    # =========================================================
    # 7. ADD HOUR AND MONTH
    # =========================================================

    if total_trips > 0:

        filtered_df["pickup_hour"] = (
            filtered_df["pickup_datetime"]
            .dt.hour
        )

        filtered_df["pickup_month"] = (
            filtered_df["pickup_datetime"]
            .dt.month
        )

    # =========================================================
    # 8. TRIPS BY HOUR
    # =========================================================

    if total_trips > 0:

        hourly = (
            filtered_df
            .groupby("pickup_hour")
            .size()
            .reindex(range(24), fill_value=0)
        )

    else:

        hourly = pd.Series(
            0,
            index=range(24)
        )

    hour_labels = hourly.index.tolist()
    hour_values = hourly.astype(int).tolist()

    # =========================================================
    # 9. MONTHLY TRIPS
    # =========================================================

    if total_trips > 0:

        monthly = (
            filtered_df
            .groupby("pickup_month")
            .size()
            .reindex(range(1, 13), fill_value=0)
        )

    else:

        monthly = pd.Series(
            0,
            index=range(1, 13)
        )

    month_labels = monthly.index.tolist()
    month_values = monthly.astype(int).tolist()

    # =========================================================
    # 10. TOP PICKUP LOCATIONS
    # =========================================================

    if total_trips > 0:

        pickup = (
            filtered_df
            .groupby("pickup_location")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )

    else:

        pickup = pd.Series(dtype=int)

    pickup_labels = pickup.index.astype(str).tolist()
    pickup_values = pickup.astype(int).tolist()

    # =========================================================
    # 11. TOP DROP-OFF LOCATIONS
    # =========================================================

    if total_trips > 0:

        dropoff = (
            filtered_df
            .groupby("dropoff_location")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )

    else:

        dropoff = pd.Series(dtype=int)

    dropoff_labels = dropoff.index.astype(str).tolist()
    dropoff_values = dropoff.astype(int).tolist()

    # =========================================================
    # 12. PAYMENT METHOD
    # =========================================================

    if total_trips > 0:

        payment = (
            filtered_df
            .groupby("payment_method")
            .size()
            .sort_values(ascending=False)
        )

    else:

        payment = pd.Series(dtype=int)

    payment_labels = payment.index.astype(str).tolist()
    payment_values = payment.astype(int).tolist()

    # =========================================================
    # 13. PASSENGER ANALYSIS
    # =========================================================

    if total_trips > 0:

        passenger = (
            filtered_df
            .groupby("passenger_count")
            .size()
            .sort_index()
        )

    else:

        passenger = pd.Series(dtype=int)

    passenger_labels = passenger.index.astype(int).tolist()
    passenger_values = passenger.astype(int).tolist()

    # =========================================================
    # 14. AVERAGE FARE BY LOCATION
    # =========================================================

    if total_trips > 0:

        fare_location = (
            filtered_df
            .groupby("pickup_location")
            .agg(
                total_trips=("fare_amount", "count"),
                average_fare=("fare_amount", "mean")
            )
            .sort_values(
                "total_trips",
                ascending=False
            )
            .head(10)
        )

    else:

        fare_location = pd.DataFrame(
            columns=[
                "total_trips",
                "average_fare"
            ]
        )

    fare_labels = (
        fare_location.index
        .astype(str)
        .tolist()
    )

    fare_values = (
        fare_location["average_fare"]
        .round(2)
        .astype(float)
        .tolist()
    )

    # =========================================================
    # 15. CONTEXT
    # =========================================================

    context = {

        # -------------------------
        # KPI
        # -------------------------

        "total_trips": total_trips,

        "avg_distance": avg_distance,

        "avg_fare": avg_fare,

        "avg_passengers": avg_passengers,


        # -------------------------
        # FILTER OPTIONS
        # -------------------------

        "pickup_locations": pickup_locations,

        "payment_methods": payment_methods,

        "passenger_counts": passenger_counts,


        # -------------------------
        # SELECTED FILTERS
        # -------------------------

        "selected_pickup": selected_pickup,

        "selected_payment": selected_payment,

        "selected_passenger": selected_passenger,


        # -------------------------
        # HOURLY
        # -------------------------

        "hour_labels": hour_labels,

        "hour_values": hour_values,


        # -------------------------
        # MONTHLY
        # -------------------------

        "month_labels": month_labels,

        "month_values": month_values,


        # -------------------------
        # PICKUP
        # -------------------------

        "pickup_labels": pickup_labels,

        "pickup_values": pickup_values,


        # -------------------------
        # DROPOFF
        # -------------------------

        "dropoff_labels": dropoff_labels,

        "dropoff_values": dropoff_values,


        # -------------------------
        # PAYMENT
        # -------------------------

        "payment_labels": payment_labels,

        "payment_values": payment_values,


        # -------------------------
        # PASSENGERS
        # -------------------------

        "passenger_labels": passenger_labels,

        "passenger_values": passenger_values,


        # -------------------------
        # FARE BY LOCATION
        # -------------------------

        "fare_labels": fare_labels,

        "fare_values": fare_values,
    }


    return render(
        request,
        "index.html",
        context
    )