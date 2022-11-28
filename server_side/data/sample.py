import time
start = time.time()
print("Response from Python File", end=' ')
time.sleep(1)
end = time.time()
print("Code Executed in: ", (end-start)*1000, "ms")