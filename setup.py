from distutils.core import setup

setup(
    name="PyRLRR",
    description="Converts MIDI files into the Paradiddle compatible RLRR format",
    license="GPL",
    author="UnofficialParadiddle",
    url="https://github.com/UnofficialParadiddle/PyRLRR",
    packages=["PyRLRR"],
    requires=["mido", "PyYAML"],
    package_data={"PyRLRR": ["midi_maps/*.yaml", "drumsets/*.rlrr"]}
)
