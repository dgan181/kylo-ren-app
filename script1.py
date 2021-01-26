import sys
print('Hello from the python file')
print('Python script successfully executed')

f= open("gen.txt","w+")
f.write("The following content was retrived from the server: \r\n")
for i in sys.argv:
    f.write(str(i)+ "\n")
f.close()
