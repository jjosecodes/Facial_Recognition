
#  swap without using a temporary variable
# swap with arithmetic operations
''' 
a , b 
a = a + b 
b = a - b 
a = a - b
'''
def SwapNumbers(a, b ):
    print (f"Before, A = {a} and B = {b}")

    a, b = b, a 
    print (f"After, A = {a} and B = {b}")

print(SwapNumbers(5,10))
#---------

# 2 rectangle area and perimeter
def Rect_area_perimeter(length, breadth):
    area = length * breadth
    perimeter = 2 * (length + breadth)
    print(f"Area = {area} and Perimeter = {perimeter}")
#test 
print(Rect_area_perimeter(5, 10))   
#---------
# 3. Check If a Number Is Positive, Negative, or Zero
def CheckNumber (num):
    sign = {
        num > 0 : "Positive",
        num < 0 : "Negative",
        num == 0 : "Zero does not have a sign"
    }
    print(sign.get(True, "Invalid input"))

CheckNumber(9)
CheckNumber(-9)
CheckNumber(0)
#---------
def grade_calc(marks):
	if marks >= 90:
		print("A")
	elif marks >= 80:
		print("B")
	elif marks >= 70:
		print("C")
	elif marks >= 60:
		print("D")
	else:
		print("F")
grade_calc(85)
grade_calc(95)
grade_calc(75)

#---------

#fibonacci series up to n numbers
def fib(n):
    if n <= 0:
        print("Enter a positive number")
        return
    a = 0 
    b = 1
    if n == 1:
        print (a) 
    else:

        print(a)
        print(b)
        for i in range(2,n):
            c = a + b
            a = b
            b = c
            print(c)

fib(4)









