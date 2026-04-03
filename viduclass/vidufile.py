filePath ="test2.txt"
file = open (filePath, "r")
text= file.read()
print(text)
file.close()