#!/usr/bin/python

import sys
import os
import csv
import subprocess

def runHB(row, font):
    args = ["hb-shape", "--no-clusters", "--no-positions",
            "--font-file=%s" %font,
            "--direction=%s" %row[0],
            "--script=%s"    %row[1],
            "--language=%s"  %row[2],
            "--features=%s"  %row[3],
            "--text=%s"      %row[4]]
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    return process.communicate()[0].strip()

def runTest(test, font):
    count = 0
    failed = {}
    passed = []
    for row in test:
        count += 1
        row[4] = ('\\' in row[4]) and row[4].decode('unicode-escape') or row[4]
        text = row[4]
        reference = row[5]
        result = runHB(row, font)
        if reference == result:
            passed.append(count)
        else:
            failed[count] = (text, reference, result)

    return passed, failed

def initTest(test, font):
    out = ""
    for row in test:
        result = runHB(row, font)
        out += "%s;%s\n" %(";".join(row), result)

    return out

if __name__ == '__main__':
    init = False
    args = sys.argv[1:]

    if len (sys.argv) > 2 and sys.argv[1] == "-i":
        init = True
        args = sys.argv[2:]

    for arg in args:
        testname = arg

        reader = csv.reader(open(testname), delimiter=';')

        test = []
        for row in reader:
            test.append(row)

        if init:
            outname = testname+".test"
            outfd = open(outname, "w")
            outfd.write("# %s\n" %fontname)
            outfd.write(initTest(test, fontname))
            outfd.close()
            sys.exit(0)

        for style in ('regular', 'bold', 'slanted', 'boldslanted'):
            fontname = 'amiri-%s.ttf' % style
            passed, failed = runTest(test, fontname)
            message = "%s: font '%s', %d passed, %d failed" %(os.path.basename(testname),
                    fontname, len(passed), len(failed))

            print message
            if failed:
                for test in failed:
                    print test
                    print "string:   \t", failed[test][0]
                    print "reference:\t", failed[test][1]
                    print "result:   \t", failed[test][2]
                sys.exit(1)
