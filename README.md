Fair warning this was made quickly so its kind of ass lmao ill optimize it later when I feel like it

YOU NEED PYTHON 3 FOR THIS!!!

Step 1: Open cmd, terminal, whatever tf you use, inside of the this repo after downloading and extracting, open the terminal where the `requirements.txt` is located. An easy way of doing so would be holding `Shift+Right Click` and then pressing `Open Powershell Window` in the menu (Fair warning: I had issues with running it in a Powershell window, however this is most likely due to my Windows 10 being jank).

Step 2: run ```pip install venv```

Step 3: run ```python -m venv .```

Step 4: run ```Scripts\\activate```

Step 5: run ```pip install -r requirements.txt```

Step 6: Get your folder structure setup. For my folder, it should contain all the song folders inside of it, so in my `Songs\` folder would be ```Song1\```, ```Song2```, etc.

Step 7: run ```python PyRLRR X``` but replace `X` with the parent directory, like mine being `Songs\` which contains all song folders

Step 8: profit

Ik this isn't too user friendly atm, but I will optimize it as time goes on.

CHANGING YAML FILE:
When you reach Step 7: just add at the end of the command, '-y X' but replace the X with the location of the YAML file.

CHANGING DRUMSET FILE:
When you reach Step 7: just add at the end of the command, '-d X' but replace the X with the location of the drumset.rlrr file.

CHANGING OUTPUT LOCATION:
When you reach Step 7: just add at the end of the command, '-o X' but replace the X with the path of where you want to put the songs. Don't worry, PyRLRR will create new directories as needed
