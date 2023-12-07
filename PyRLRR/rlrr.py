import os
import json
import shutil
import configparser
import yaml
from time import sleep
from .midiconvert import MidiConverter


class RLRR_Metadata():
    def __init__(self, directory):
        self.VERSION = 0.6

        self.title = "(new)"
        self.description = ""
        self.coverImagePath = ""
        self.artist = ""
        self.album = ""
        self.creator = ""
        self.length = 0.0
        self.complexity = 0
        self.difficulty = "Easy"
        
        self.chartDir = directory
        
        self.filePath = None
        if (os.path.exists(directory) == False):
            return
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
            "drumRLRR": os.path.join(os.path.dirname(__file__), "drumsets", "defaultset.rlrr"),
            "yamlFilePath": os.path.join(os.path.dirname(os.path.abspath(__file__)), "midi_maps", "rhythm_game_mapping_gh.yaml"),
            "verbose": False,
            "strict": False,
            "failFree": False,
            "tracks": ["DRUMS"]
        }
        self._instKind = "Drums"

        self.songTracks = [""] * 5
        self.drumTracks = [""] * 4

        self.instruments = [{}]
        self.events = [{}]
        self.bpmEvents = []

        self._mc = MidiConverter()

        self.calibrationOffset = 0.0
        
        self.metadata = RLRR_Metadata(directory)
        if (os.path.exists(directory)):
            self.parse_dir_info()


    def parse_midi(self, midiPath, track_index = -1):
        midiConvert = self._mc
        midiConvert.difficulty = self.metadata.difficulty

        midiConvert.analyze_drum_set(self.options["drumRLRR"])
                     
        midiConvert.midi_file = midiPath
        with open(self.options["yamlFilePath"]) as yamlOpen:
            yamlFile = yaml.load(yamlOpen, Loader=yaml.FullLoader)
            midiConvert.create_midi_map(yamlFile)
            midiConvert.get_tracks()
            if (track_index == -1):
                (default_track, track_index) = midiConvert.get_drum_track(self.options["tracks"])
                if track_index == -1:
                    return 1
            midiConvert.convert_track_index = track_index
            midiConvert.track_to_convert = default_track
        
        midiConvert.analyze_midi_file()
        self.instruments = midiConvert.out_dict["instruments"]
        self.events = midiConvert.out_dict["events"]
        self.bpmEvents = midiConvert.out_dict["bpmEvents"]

        # print(midiConvert.midi_track_names)

        return 0

    # Parses all of the content within the chart directory into the class instance
    def parse_dir_info(self):
        chartDirFiles = [x for x in os.listdir(self.metadata.chartDir)]
        dI = 0
        sI = 0
        
        for file in chartDirFiles:
            base = os.path.basename(file)
            if base.startswith("album") and (base.endswith('.png') or base.endswith('.jpg')):
                self.metadata.coverImagePath = file
            elif base.endswith('.ogg') or base.endswith('.mp3') or base.endswith('.wav'):
                if base.lower().startswith("drum"):
                    self.drumTracks[dI] = file
                    dI = dI+1
                else:
                    self.songTracks[sI] = file
                    sI = sI+1
        
        

    def copy_files(self, outputDir):
        coverImg = os.path.join(self.metadata.chartDir, self.metadata.coverImagePath)
        if (os.path.isfile(coverImg)):
            shutil.copyfile(coverImg, os.path.join(outputDir, self.metadata.coverImagePath))
        for songTrack in self.songTracks:
            sT = os.path.join(self.metadata.chartDir, songTrack)
            if (os.path.isfile(sT)):
                shutil.copyfile(sT, os.path.join(outputDir, songTrack))
        for drumTrack in self.drumTracks:
            dT = os.path.join(self.metadata.chartDir, drumTrack)
            if (os.path.isfile(dT)):
                shutil.copyfile(dT, os.path.join(outputDir, drumTrack))


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
                "songTracks": [os.path.basename(x) for x in self.songTracks if os.path.isfile(os.path.join(self.metadata.chartDir, x))],
                "drumTracks": [os.path.basename(x) for x in self.drumTracks if os.path.isfile(os.path.join(self.metadata.chartDir, x))],
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
    
        with open(os.path.join(outputDir, self.metadata.artist + ' - ' + self.metadata.title +"_"+self.metadata.difficulty+".rlrr"), "w") as outfile:
            outfile.write(rlrr)
