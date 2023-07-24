
file_path = "example.txt"  # Replace "example.txt" with the desired file name and extension

# Opening the file in 'w' mode to create it or overwrite it if it already exists
with open(file_path, 'w') as file:
    file.write("Hello, this is some content in the file.\n")
    file.write("You can add more lines if you want.\n")

print("File created successfully!")
