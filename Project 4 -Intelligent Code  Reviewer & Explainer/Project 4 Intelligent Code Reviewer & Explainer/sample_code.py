# Sample Python file with some issues
def calculate_average(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total / len(numbers)

def find_max(numbers):
    max_num = 0
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

# Bug: division by zero if empty list
avg = calculate_average([])
print(f"Average: {avg}")

# Bug: max_num initialized to 0, fails for negative numbers
max_val = find_max([-5, -2, -10])
print(f"Max: {max_val}")

# Bug: using range(len()) is inefficient
def calculate_sum(numbers):
    total = 0
    for i in range(len(numbers)):
        total += numbers[i]
    return total