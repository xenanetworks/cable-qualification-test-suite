Latency & Frame Loss Test
===========================================

The Latency & Frame Loss Test collects the latency and frame loss data. The test is performed to ensure that the cable meets the required specifications.

Setup
-----

1. Start traffic rate (percentage of line rate)
2. End traffic rate (percentage of line rate)
3. Step size (percentage of line rate)
4. Packet sizes
5. Test duration


Method
----------

1. Create an Ethernet stream with a packet size.
2. Start traffic with the start rate.
3. Measure latency and frame loss.
4. Increase traffic rate by step size.
5. Repeat steps 2-3 until the end rate is reached.
6. Repeat the above for each packet size.