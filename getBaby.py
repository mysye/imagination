#!/usr/bin/python
# Python version used was v2.7.5 on Fedora 20
# Written by Stephane Ye - 09/07/2015

# importing modules
import os
import sys
import re
import pycurl


# Define main() function

def main(argv):


    # Arguments control
    # if no argument or incorrect number of arguments are given, the below is displayed
    # ./getBaby.py [name] [start_year] [end_year]

    if len(argv) != 4:
        print("\n\t" + argv[0] + " [name] [start_year] [end_year]\n")
        sys.exit(1)


    # Parsing arguments
    name = argv[1]
    startYear = argv[2]
    endYear = argv[3]


    # Make up the name of the cache file to which the HTTP response will be printed and stored for a specific run
    # eg. "Jordan1880-2010.html"
    outfileHtml = argv[1] + argv[2] + '-' + argv[3] + '.html'


    # Make up a string of arguments that will be passed to the pycurl.Curl() method
    # eg. "name=Jordan&start=1880&sex=M"
    # Please note that the end year can't be passed to the HTTP request, it will be processed only after the response is received
    # See later section of the programme
    postArgvs = 'name=' + argv[1] + '&start=' + argv[2] + '&sex=' + 'M'


    # Test if the content cache file already exists in case the same command has been run before
    # in which case, the programme will not make a new HTTP run, instead, it will use the cached html file as input data
    if not os.path.exists(outfileHtml):
        c = pycurl.Curl()
        c.setopt(c.URL, 'http://www.socialsecurity.gov/cgi-bin/babyname.cgi')
        c.setopt(c.POSTFIELDS, postArgvs)
        
        with open(outfileHtml, 'w') as outfile:
            c.setopt(c.WRITEFUNCTION, outfile.write)
            c.perform()
        outfile.close()


    # Open the HTTP cache file and load each line into the list "lines"
    lines = []
    with open(outfileHtml, "r") as file:
        for line in file:
            lines.append(line)
    file.close()


    # We want extract lines containing Year/Rank only, the below re pattern needs to be compile for use further down
    pattern = re.compile('.*align\=\"center\"\>(\d+)\<\/td\>.*')


    # Define a function that will take one line at a time and only return it if it matches the re "pattern"
    def filter(line):
        matched = pattern.match(line)
        if matched:
            return matched.group(1)


    # As a result the below list "values" will contain only data lines as a result of filtering
    values = [x for x in map(filter, lines) if x]


    # Convert the list "values" into one that contains (Year, Rank) tuples such as [('1989', '837'), ('1987', '921'), ('1986', '930'),....]
    valuesPairs = [(values[i], values[i+1]) for i in range(0, len(values), 2)]


    # Calculate the mean average of a given name, start year, end year
    # The below for loop will drop any year/rank pairs beyond the end year
    sumRankByYear = 0
    numYears = 0
    endYear = argv[3]
    for i in range(len(valuesPairs)):
	if valuesPairs[i][0] <= endYear:
            sumRankByYear += int(valuesPairs[i][1])
            numYears += 1


    # Print the results on a successful run
    if numYears != 0:
        print ("Between %s and %s the average popularity rank of the name %s was %6.2f" % (startYear, endYear, name, sumRankByYear/float(numYears)))
    # If no result is received, print the result as "0", otherwise the above print will throw an exception on division by 0
    else:
        print ("Between %s and %s the average popularity rank of the name %s was %6.2f" % (startYear, endYear, name, 0))


if __name__ == "__main__":
    main(sys.argv[0:])

