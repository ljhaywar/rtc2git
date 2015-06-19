import sys
from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError

import shouter


logcommands = False


def execute(command, outputfile=None, openmode="w"):
    shout_command_to_log(command, outputfile)
    if not outputfile:
        return call(command, shell=True)
    else:
        with open(outputfile, openmode) as file:
            return call(command, stdout=file, shell=True)


def getoutput(command):
    shout_command_to_log(command)
    try:
        outputasbytestring = check_output(command, shell=True)
    except CalledProcessError as e:
        shouter.shout(e)
        outputasbytestring = e.output
    output = outputasbytestring.decode(sys.stdout.encoding).splitlines()
    strippedlines = []
    for line in output:
        cleanedline = line.strip()
        if cleanedline:
            strippedlines.append(cleanedline)
    return strippedlines


def quote(stringtoquote):
    stringtoquote = stringtoquote.replace('\"', "'")  # replace " with '
    quotedstring = '\"' + stringtoquote + '\"'
    return quotedstring


def shout_command_to_log(command, outputfile=None):
    if logcommands:
        logmessage = "Executed Command: " + quote(command)
        if outputfile:
            shouter.shout(logmessage + " --> " + outputfile)
        else:
            shouter.shout(logmessage)
