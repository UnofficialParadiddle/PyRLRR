import os
import json
import shutil
import configparser
import yaml
from time import sleep
from midiconvert import MidiConverter, Difficulties


class RLRR_Metadata():
    def __init__(self, directory):
        self.VERSION = 0.6

        self.title = ""
        self.description = ""
        self.coverImagePath = ""
        self.artist = ""
        self.creator = ""
        self.length = 0.0
        self.complexity = 0
        
        self.chartDir = directory
        
        self.filePath = None
        for file in os.listdir(directory):
            if file.endswith(".ini") and "song" in os.path.basename(file).lower():
                self.filePath = file
        if self.filePath == None:
            return
        
        songINI = configparser.ConfigParser()
        songINI.read(os.path.join(directory, self.filePath))

        sectName = "Song"
        iniSects = songINI.sections()
        if "song" in iniSects:
            sectName = "song"
        
        self.length = (songINI.getfloat(sectName, "song_length")/1000.0) 
        self.title = songINI.get(sectName, "name")
        self.artist = songINI.get(sectName, "artist")
        self.creator = songINI.get(sectName, "charter") 


class RLRR():
    def __init__(self, directory):
        self.options = {
            "drumRLRR": os.path.join(os.path.dirname(__file__), "defaultset.rlrr"),
            "yamlFilePath": os.path.join(os.path.dirname(os.path.abspath(__file__)), "rhythm_game_mapping_gh.yaml"),
            "verbose": False,
            "strict": False,
            "failFree": False,
            "tracks": ["drums", "guitar"]
        }
        self._instKind = "Drums"

        self.songTracks = []
        self.drumTracks = []

        self.instruments = [{}]
        self.events = [{}]
        self.bpmEvents = []

        self.calibrationOffset = 0.0
        
        self.metadata = RLRR_Metadata(directory)
        self.parse_dir_info()


    def parse_midi(self, midiPath):
        midiConvert = MidiConverter()
        midiConvert.difficulty = Difficulties(self.metadata.complexity).name

        midiConvert.analyze_drum_set(self.options["drumRLRR"])
                     
        midiConvert.midi_file = midiPath
        with open(self.options["yamlFilePath"]) as yamlOpen:
            yamlFile = yaml.load(yamlOpen, Loader=yaml.FullLoader)
            midiConvert.create_midi_map(yamlFile)
            (default_track, track_index) = midiConvert.get_default_midi_track(self.options["tracks"])
            if track_index == -1:
                return 1
            midiConvert.convert_track_index = track_index
            midiConvert.track_to_convert = default_track
        
        midiConvert.analyze_midi_file()
        self.instruments = midiConvert.out_dict["instruments"]
        self.events = midiConvert.out_dict["events"]
        self.bpmEvents = midiConvert.out_dict["bpmEvents"]

        print(midiConvert.midi_track_names)

        return 0

    # Parses all of the content within the chart directory into the class instance
    def parse_dir_info(self):
        chartDirFiles = [x for x in os.listdir(self.metadata.chartDir)]
        
        for file in chartDirFiles:
            base = os.path.basename(file)
            if base.startswith("album") and (base.endswith('.png') or base.endswith('.jpg')):
                self.metadata.coverImagePath = file
            elif base.endswith('.ogg') or base.endswith('.mp3') or base.endswith('.wav'):
                if base.lower().startswith("drum"):
                    self.drumTracks.append(file)
                else:
                    self.songTracks.append(file)
        

    def copy_files(self, outputDir):
        shutil.copyfile(os.path.join(self.metadata.chartDir, self.metadata.coverImagePath), os.path.join(outputDir, self.metadata.coverImagePath))
        for songTrack in self.songTracks:
            shutil.copyfile(os.path.join(self.metadata.chartDir, songTrack), os.path.join(outputDir, songTrack))
        for drumTrack in self.drumTracks:
            shutil.copyfile(os.path.join(self.metadata.chartDir, drumTrack), os.path.join(outputDir, drumTrack))


    def output_rlrr(self, outputDir):        
        rlrr_dict = {
            "version": self.metadata.VERSION,
            "recordingMetadata": {
                "title": self.metadata.title,
                "description": self.metadata.description,
                "coverImagePath": os.path.basename(self.metadata.coverImagePath),
                "artist": self.metadata.artist,
                "creator": self.metadata.creator,
                "length": self.metadata.length,
                "complexity": self.metadata.complexity
            },
            "audioFileData": {
                "songTracks": [os.path.basename(x) for x in self.songTracks],
                "drumTracks": [os.path.basename(x) for x in self.drumTracks],
                "calibrationOffset": self.calibrationOffset
            },
            "instruments": self.instruments,
            "events": self.events,
            "bpmEvents": self.bpmEvents
        }

        with open(self.options["drumRLRR"], "r") as drumsetRLRR:
            drumset = json.load(drumsetRLRR)
            self.instruments = drumset["instruments"]

        rlrr = json.dumps(rlrr_dict, indent=4)

        os.makedirs(outputDir, exist_ok = True)
    
        with open(os.path.join(outputDir, os.path.basename(self.metadata.chartDir)+"_"+Difficulties(self.metadata.complexity).name+".rlrr"), "w") as outfile:
            outfile.write(rlrr)