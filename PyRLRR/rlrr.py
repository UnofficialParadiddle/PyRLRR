import os
import json
import shutil
import configparser
import chparse
import yaml
from time import sleep
from midiconvert import MidiConverter


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
        
        filePath = "song.ini"
        for file in os.listdir(directory):
            if file.endswith(".ini"):
                filePath = file
        
        songINI = configparser.ConfigParser()
        songINI.read(os.path.join(directory, filePath))

        sectName = "Song"
        iniSects = songINI.sections()
        if iniSects.count('song') > 0:
            sectName = "song"
        
        self.length = songINI.getfloat(sectName, "song_length") 
        self.title = songINI.get(sectName, "name")
        self.artist = songINI.get(sectName, "artist")
        self.creator = songINI.get(sectName, "charter") 

class RLRR():
    def __init__(self, directory):
        self.options = {
            "drumRLRR": os.path.join(os.path.dirname(__file__), "defaultset.rlrr"),
            "yamlFilePath": os.path.join(os.path.dirname(os.path.abspath(__file__)), "rhythm_game_mapping_gh.yaml")
        }
        self.metadata = RLRR_Metadata

        self._instKind = "Drums"

        self.songTracks = []
        self.drumTracks = []

        self.instruments = [{}]
        self.events = [{}]
        self.bpmEvents = []

        self.calibrationOffset = 0.0
        
        
        self.metadata = RLRR_Metadata(directory)
        self.parse_dir_info()

        # This is used to set the instruments
        with open(self.options["drumRLRR"], "r") as drumsetRLRR:
            drumset = json.load(drumsetRLRR)
            self.instruments = drumset["instruments"]
        
    # !!! INCOMPLETE !!!
    def parse_chart(self, chartPath):
        with open(chartPath, encoding='utf-8') as chartFile:
            chart = chparse.load(chartFile)

        with open(chartFile, encoding='utf-8') as chartFile:
            content = chartFile.read()
            i = 0
            while True:
                splitLine = content.split('[')[i+1]
                if "Song" not in splitLine.split(']')[i]:
                    i = i+1
                    continue
                
                songData = content.split(']')[i+1]
                songData = songData.split('{')[1]
                songData = songData.split('}')[0]
                
                # TODO: I now know that ConfigParser allows you to remove the section entirely and just put DEFAULT
                songData = "[Song]\n" + songData
                songConfig = configparser.ConfigParser()
                songConfig.read_string(songData)
                for key in songConfig.items("Song"):
                    if "stream" in key[0].lower():
                        if "drum" in key[0].split("Stream")[0].lower():
                            self.drumTracks.append(songConfig.get("Song", key[0]).split('"')[1])
                        else:
                            self.songTracks.append(songConfig.get("Song", key[0]).split('"')[1])
                break
        
        # Sets all of the BPM Events, avoiding all the Time Signature ones as well
        for syncTrack in chart.sync_track:
            if syncTrack.kind == chparse.flags.BPM:
                bpmEvent = {
                    "bpm": float(syncTrack.value/1000),
                    "time": float(syncTrack.time)
                }
                self.bpmEvents.append(bpmEvent)

        difficulties = [chparse.flags.EXPERT, chparse.flags.HARD, chparse.flags.MEDIUM, chparse.flags.EASY, chparse.flags.NA]
        instruments = [chparse.flags.GUITAR, chparse.flags.DRUMS]
        
        for diff in difficulties:
            # For all the instruments I will do, which the note conversion equivalent will be placed inside a dict
            for inst in instruments:
                pass
    
    def parse_midi(self, midiPath):
        midiConvert = MidiConverter()
        
        if self.metadata.complexity == 1:
            midiConvert.difficulty = "Easy"
        elif self.metadata.complexity == 2:
            midiConvert.difficulty = "Medium"
        elif self.metadata.complexity == 3:
            midiConvert.difficulty = "Hard"
        else:
            midiConvert.difficulty = "Expert"
        
        midiConvert.analyze_drum_set(self.options["drumRLRR"])
                     
        midiConvert.midi_file = midiPath
        with open(self.options["yamlFilePath"]) as yamlOpen:
            yamlFile = yaml.load(yamlOpen, Loader=yaml.FullLoader)
            midiConvert.create_midi_map(yamlFile)
            (default_track, track_index) = midiConvert.get_default_midi_track()
            midiConvert.convert_track_index = track_index
        
        midiConvert.analyze_midi_file()
        self.instruments = midiConvert.out_dict["instruments"]
        self.events = midiConvert.out_dict["events"]
        self.bpmEvents = midiConvert.out_dict["bpmEvents"]
        
        del midiConvert

    # Parses all of the content within the chart directory into the class instance
    def parse_dir_info(self):
        chartDirFiles = [x for x in os.listdir(self.metadata.chartDir)]
        
        for file in chartDirFiles:
            base = os.path.basename(file)
            if base.startswith("album") and (base.endswith('.png') or base.endswith('.jpg')):
                self.metadata.coverImagePath = file
            elif base.endswith('.ogg') or base.endswith('.mp3'):
                if base.lower().startswith("drum"):
                    self.drumTracks.append(file)
                else:
                    self.songTracks.append(file)
        

    def output(self, outputDir):        
        difficulties = ["Easy", "Medium", "Hard", "Expert"]

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
        rlrr = json.dumps(rlrr_dict, indent=4)

        os.makedirs(outputDir, exist_ok = True)
        
        # PERFORMANCE: I feel like there is a better way of doing things, but i'm ungodly tired
        # diff = "Expert"
        # if self.metadata.complexity == 1:


        # TODO: There should be a better way of doing things
        with open(os.path.join(outputDir, os.path.basename(self.metadata.chartDir)+"_"+difficulties[self.metadata.complexity-1]+".rlrr"), "w") as outfile:
            outfile.write(rlrr)

        shutil.copyfile(os.path.join(self.metadata.chartDir, self.metadata.coverImagePath), os.path.join(outputDir, self.metadata.coverImagePath))
        for songTrack in self.songTracks:
            shutil.copyfile(os.path.join(self.metadata.chartDir, songTrack), os.path.join(outputDir, songTrack))
        for drumTrack in self.drumTracks:
            shutil.copyfile(os.path.join(self.metadata.chartDir, drumTrack), os.path.join(outputDir, drumTrack))
