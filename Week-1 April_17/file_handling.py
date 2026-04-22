with open("textfile.txt", "r") as f:
    data = f.read()

data = data.split()
word_count = len(data)
print(f"The number of words in the file is: {word_count}")