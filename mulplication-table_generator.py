print("Welcome to Multiplication Table Generator")
number = int(input("Enter any number: "))

multiplier = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
for i in multiplier:
    print(f"{number} * {i} = {number*i}")
print("The End")