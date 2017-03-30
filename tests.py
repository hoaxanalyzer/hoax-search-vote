import collector
import time

start = time.time()
(collector.do("flat earth"))

stop = time.time()
print("Time elapsed: " + str(stop-start))