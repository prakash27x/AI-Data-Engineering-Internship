input_number = input("Enter a list of numbers separated by spaces: ")

# Convert to integers
number_list = input_number.split()
number_list = [int(num) for num in number_list]

def find_max_number(num_list):
    max_no = num_list[0]
    
    for number in num_list:
        if number > max_no:
            max_no = number
    return max_no 

max_no = find_max_number(number_list)

print("The maximum number in the list is:", max_no)