
# Congestion Control Module

## Project
Computer Networks - Congestion Control using Leaky Bucket Algorithm

## Description
This module simulates network traffic congestion using the
Leaky Bucket algorithm. It controls the rate of packet transmission
and models packet queues, packet arrivals, and packet drops.

## Features
- Simulates packet arrivals at different time intervals
- Implements a FIFO packet queue
- Limits queue size using bucket capacity
- Controls packet transmission at a fixed output rate
- Detects congestion and packet drops
- Displays transmission statistics and packet drop percentage

## Requirements
- Python 3.x

## How to Run
Open a terminal inside the congestion_control folder.

Run:

python leaky_bucket.py

Enter the bucket capacity, output rate, simulation duration,
and packet arrivals when prompted.

## Algorithm
1. Initialize a bucket with a fixed capacity.
2. Accept incoming packets while queue space is available.
3. Drop packets when the bucket is full.
4. Transmit packets at a constant output rate.
5. Display queue status and congestion statistics.

## Module Owner
Priyanka