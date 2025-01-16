#check if prime
def is_prime(num):
    if num <= 1:   
        return False
    for i in range(2, int(num**0.5) + 1):  # 
        if num % i == 0:   
            return False
    return True

#count vowels in a string
def count_vowels(s):
    vowels = 'aeiou'
    count = sum(1 for char in s.lower() if char in vowels)  
    return count

# Test cases
print(count_vowels("Hello World"))  
print(count_vowels("Python"))       



# Largest and Smallest Numbers in a List
def find_largest_smallest(lst):
    if not lst: 
        return "List is empty."
    return max(lst), min(lst)

# Test cases
print(find_largest_smallest([3, 5, 1, 9, 2]))  
print(find_largest_smallest([-10, 0, 5, 100])) 


def calculate_average(marks_dict):
    if not marks_dict:  # Check if the dictionary is empty
        return "No students in the dictionary."
    total_marks = sum(marks_dict.values())  # Sum of marks
    average = total_marks / len(marks_dict)  # Calculate average
    return average

def is_palindrome(s):
    s = s.lower()  
    return s == s[::-1]  
student_marks = {"Alice": 85, "Bob": 78, "Charlie": 92}
print(calculate_average(student_marks))  
# 85
print(calculate_average({}))           
