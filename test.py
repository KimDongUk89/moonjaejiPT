import pdftotext

file = open('myflask/files/02Graphics+Systems+and+Models.pdf', 'rb')
fileReader = pdftotext.PDF(file)

print(fileReader[5])