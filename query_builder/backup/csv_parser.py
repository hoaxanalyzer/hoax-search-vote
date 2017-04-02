"""
CSV PARSER

Parsing csv file

"""

import csv, re

filename_load = "../dataset/fake.csv"
filename_save = "../dataset/fake-parsed.csv"

csvfile_load = open(filename_load, 'rb')
csvfile_save = open(filename_save, 'w')

dataset = csv.reader(csvfile_load, delimiter=',', quotechar='"')
i = 0
for row in dataset:
	if (i==1):
		print "1"
	elif (i==3):
		break
	else:
		for j in range(0, len(row)):
			if j==4 or j==5:
				data = row[j]
				data = data.decode("ascii", "replace").replace(u"\ufffd", "_").replace("___", "'") 
				print data
				# print "string" + row[j]
				# str = ""
				# for k in row[j]:
				# 	if k.isalnum():
				# 		str.join(k)
				# 	else:
				# 		str.join("'")
				# print str
	i = i + 1
	print i