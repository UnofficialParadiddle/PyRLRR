import os
import sys
import logging
from supports_color import supportsColor 
import argparse as ap
from rlrr import RLRR
from pathlib import Path

convColor = "Converting: "
continueColor = "Continuing Conversion..."
failedColor = "FAILED: "
successColor = "Success: "
if supportsColor.stdout:
    successColor = "\033[1;32mSuccess: \033[0;37m"
    failedColor = "\033[1;31mFAILED: \033[0;37m"
    convColor = "\033[1;33mConverting: \033[0;37m"
    continueColor = "\033[1;34mContinuing Conversion...\033[0;37m"


parser = ap.ArgumentParser()
parser.add_argument('-d', '--drumset', action="store", dest="drumset")
parser.add_argument('-o', '--output', action="store", dest="outputDir")
parser.add_argument('-y', '--yaml', action="store", dest="yamlPath")
parser.add_argument('-v', '--verbose', action="store_true", dest="isVerbose")
args, unknown = parser.parse_known_args()

if args.outputDir and not os.path.isdir(args.outputDir):
    os.makedirs(args.outputDir)
if args.drumset and not os.path.isfile(args.drumset):
    print(failedColor + "Drumset doesn't exist - " + args.drumset)
if args.yamlPath and not os.path.isfile(args.yamlPath):
    print(failedColor + "YAML doesn't exist - " + args.yamlPath)


def _throwErr(message, e = None):
    print(failedColor + message)
    if args.isVerbose == True:
        print(e)


if __name__ == "__main__":
    if len(unknown) == 0:
        _throwErr('No batch path given')
        exit(1)

    if not os.path.isdir(unknown[0]):
        _throwErr("Not a directory - " + unknown[0])
        exit(1)

    batchDir = Path(unknown[0])
    if not os.path.isdir(batchDir):
        _throwErr("Batch directory does not exist or is invalid - " + batchDir)
        exit(1)

    # Gets all of the songs within the directory given
    subdirectories = [x.path for x in os.scandir(batchDir) if os.path.isdir(x)]
    difficulties = ["Easy", "Medium", "Hard", "Expert"]
    
    successful = 0
    failed = 0
    
    for directory in subdirectories:
        baseDir = os.path.basename(directory)
        print(convColor + baseDir)

        try:
            convertedChart = RLRR(directory)

            if args.drumset:
                convertedChart.options["drumRLRR"] = args.drumset
            if args.yamlPath:
                convertedChart.options["yamlFilePath"] = args.yamlPath

            filePath = ""
            for file in os.listdir(directory):
                if file.endswith(".mid"):
                    filePath = file
                    break

            if not filePath.endswith(".mid"):
                _throwErr("No MIDI file found within directory - " + directory)
                    

            outputDir = os.path.join(os.getcwd(), baseDir)
            for comp in range(0, len(difficulties)):
                convertedChart.metadata.complexity = comp+1
                
                convertedChart.parse_midi(os.path.join(directory, filePath))

                if args.outputDir:
                    outputDir = os.path.join(args.outputDir, baseDir)
                convertedChart.output_rlrr(outputDir)

            convertedChart.copy_files(outputDir)

            if not args.isVerbose and supportsColor.stdout: 
                sys.stdout.write("\033[F")
            print(successColor + baseDir)
            successful = successful + 1
        except EOFError:
            _throwErr(baseDir + "\n\t- EOFError: Unexpected EOF in MIDI file" + "\n\t- Please rebuild MIDI file and try again")
            print(continueColor)
            
            failed = failed + 1
            continue
        
    print("\nConversion Complete")
    print(successColor + str(successful))
    print(failedColor + str(failed))