import os
import argparse as ap
from rlrr import RLRR
from pathlib import Path


parser = ap.ArgumentParser()
parser.add_argument('-d', '--drumset', action="store", dest="drumset")
parser.add_argument('-o', '--output', action="store", dest="outputDir")
parser.add_argument('-y', '--yaml', action="store", dest="yamlPath")
args, unknown = parser.parse_known_args()

if args.outputDir and not os.path.isdir(args.outputDir):
    os.makedirs(args.outputDir)
if args.drumset and not os.path.isfile(args.drumset):
    print("FAILED: Drumset doesn't exist - " + args.drumset)
if args.yamlPath and not os.path.isfile(args.yamlPath):
    print("FAILED: YAML doesn't exist - " + args.yamlPath)


if __name__ == "__main__":
    if len(unknown) == 0:
        print('FAILED: No batch path given')
        exit(1)

    if not os.path.isdir(unknown[0]):
        print("FAILED: Not a directory - " + unknown[0])
        exit(1)
        
    batchDir = Path(unknown[0])
    
    # Gets all of the songs within the directory given
    subdirectories = [x.path for x in os.scandir(batchDir) if os.path.isdir(x)]
    difficulties = ["Easy", "Medium", "Hard", "Expert"]
    for directory in subdirectories:
        for comp in range(0, len(difficulties)):
            try:
                convertedChart = RLRR(directory)
                convertedChart.metadata.complexity = comp
                
                if args.drumset:
                    convertedChart.options["drumRLRR"] = args.drumset
                if args.yamlPath:
                    convertedChart.options["yamlFilePath"] = args.yamlPath

                filePath = "notes.mid"
                    
                for file in os.listdir(directory):
                    if file.endswith(".mid") or file.endswith(".chart"):
                        filePath = file
                        break

                if filePath.endswith(".mid"):
                    convertedChart.parse_midi(os.path.join(directory, filePath))
                else:
                    convertedChart.parse_chart(os.path.join(directory, filePath))

                if not args.outputDir:
                    convertedChart.output(os.path.join(os.getcwd(), os.path.basename(directory)))
                else:
                    convertedChart.output(os.path.join(args.outputDir, os.path.basename(directory)))
            except:
                print("\nSong Conversion Failed, skipping to next song")
                continue