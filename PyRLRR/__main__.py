import os
import sys
import logging
import argparse as ap
from rlrr import RLRR
from pathlib import Path

convColor = "Converting: "
continueColor = "Continuing Conversion..."
failedColor = "FAILED: "
successColor = "Success: "
warnColor = "WARNING: "

parser = ap.ArgumentParser()
parser.add_argument('-d', '--drumset', action="store", dest="drumset") # set custom drumset.rlrr
parser.add_argument('-o', '--output', action="store", dest="outputDir") # set output directory for converted files
parser.add_argument('-y', '--yaml', action="store", dest="yamlPath") # set custom yaml file

# TODO: This needs made
parser.add_argument('-v', '--verbose', action="store_true", dest="isVerbose") # extra debug info for files

parser.add_argument('-s', '--strict', action="store_true", dest="isStrict") # must contain INI and audio files
parser.add_argument('-f', '--fail-free', action="store_true", dest="isContinueConv") # will stop conversion if one chart were to fail
parser.add_argument('--track-type', action="store", dest="trackType") # must abide by certain track type
parser.add_argument('--strict-track-type', action="store", dest="strictTrackType")
args, unknown = parser.parse_known_args()


def _throwErr(message, e = None):
    print(failedColor + message)
    if args.isVerbose == True:
        print(e)
    if args.isStrict:
        print("Strict Enabled")
        exit(1)
    if not args.isContinueConv:
        print("Failsafe Enabled")
        exit(1)

if args.outputDir and not os.path.isdir(args.outputDir):
    os.makedirs(args.outputDir)
if args.drumset and not os.path.isfile(args.drumset):
    _throwErr("Drumset doesn't exist - " + args.drumset)
if args.yamlPath and not os.path.isfile(args.yamlPath):
    _throwErr("YAML doesn't exist - " + args.yamlPath)

difficulties = ["Easy", "Medium", "Hard", "Expert"]

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

    successful = 0
    failed = 0
    
    disableOverwrite = False
    if args.isVerbose:
        disableOverwrite = True

    for directory in subdirectories:
        baseDir = os.path.basename(directory)
        print(convColor + baseDir)
            
        convertedChart = RLRR(directory)
        if convertedChart.metadata.filePath == None:
            if args.isStrict == True:
                _throwErr("Couldn't find .ini file for metadata - Strict enabled")
                exit(1)
            else:
                print(warnColor + "Couldn't find .ini file for metadata - Skipping")
                disableOverwrite = True

        if args.drumset:
            convertedChart.options["drumRLRR"] = args.drumset
        if args.yamlPath:
            convertedChart.options["yamlFilePath"] = args.yamlPath
        
        if args.trackType:
            convertedChart.options["tracks"].append(args.trackType)
        if args.strictTrackType:
            convertedChart.options["tracks"] = [args.strictTrackType]

        filePath = ""
        for file in os.listdir(directory):
            if file.endswith(".mid"):
                filePath = file
                break

        if not filePath.endswith(".mid"):
            _throwErr("No MIDI file found within directory - " + directory + "\nSkipping Song")
            print(continueColor)
            failed = failed + 1
            continue
                    

        outputDir = os.path.join(os.getcwd(), baseDir)
        if args.outputDir:
            outputDir = os.path.join(args.outputDir, baseDir)

        res = 0
        for diff in difficulties:
            convertedChart.metadata.difficulty = diff
            res = convertedChart.parse_midi(os.path.join(directory, filePath))
            if res == 1:
                _throwErr("Couldn't find track(s) within MIDI file")
                print(continueColor)
                failed = failed + 1
                break

            convertedChart.output_rlrr(outputDir)
        if res != 0:
            continue

        convertedChart.copy_files(outputDir)
        print(successColor + baseDir)
        successful = successful + 1
        
    print("\nConversion Complete")
    print(successColor + str(successful))
    print(failedColor + str(failed))
