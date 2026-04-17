import math

full_marks = int(input("Enter Full Marks:"))
obtained_marks = float(input("Enter Obtained Marks:"))

percentage = (obtained_marks/full_marks)*100

if percentage >= 90:
    print("You have achieved Grade: A")
elif percentage >= 80 and percentage <= 89:
    print("You have achieved Grade: B")
elif percentage >= 70 and percentage <= 79:
    print("You have achieved Grade: C")
elif percentage >= 60 and percentage <= 69:
    print("You have achieved Grade: D")
else:
    print("You have Failed this exam.")