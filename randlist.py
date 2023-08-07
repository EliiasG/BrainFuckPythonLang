import random
nums = list(range(100))
random.shuffle(nums)
r = []
for i in range(len(nums)):
    r += [f"sto {nums[i]} apples {i}"]
print("\n".join(r))