"""
A program written in Python to test against the system as an example of all
functions and/or capabilites that we are trying to accomplish with Vocoder
using examples from https://www.w3schools.com/python/python_conditions.asp
"""
# testing CNV case. say "create new variable"
n = 1
print("test case 1 CNV:1", n)

# testing AOV case. say "assign old variable"
n = 2
print("test case 2 AOV:2", n)

# testing RS case. say "return statement"
def rs_functionVar():
  return n
def rs_functionNum():
  return 3
def rs_functionEq():
  return n+1
print("test case 3 RS,var:2", rs_functionVar())
print("test case 3 RS,num:3", rs_functionNum())
print("test case 3 RS,eq:3", rs_functionEq())

# testing CFL case. say "create for loop"
print("test case 4 CFL start: print 0 - 5")
for x in range(6):
  print(x)
print("test case 4 CFL end.")

# testing CWL case. say "create while loop"
print("test case 5 CWL start: print 2 - 5")
while n < 6:
  print(n)
  n += 1
print("test case 5 end.")

# testing CIF case. say "create if statement"
print("test case 6 CIF start:")
a = 33
b = 200
if b > a:
  print("b is greater than a")
print("test case 6 end.")

# testing CEIF case. say "create else-if statement"
print("test case 7 CEIF start:")
a = 33
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")
print("test case 7 end.")

# testing CEF case. say "create else statement"
print("test case 8 CEF start:")
a = 200
b = 33
if b > a:
  print("b is greater than a")
elif a == b:
  print("a and b are equal")
else:
  print("a is greater than b")
print("test case 8 end.")

# testing CA case. say "create array"
print("test case 9 CA start:")
cars = ["Ford", "Volvo", "BMW"]
for x in cars:
  print(x)
print("test case 9 end.")
