from retry_policy import should_retry
assert should_retry("GET",503,1)
assert not should_retry("POST",503,1)
assert not should_retry("GET",503,3)
print("visible tests PASS")
