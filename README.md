# Towers of Babble Word Finder
This is a word finder inspired by similar programs for Scrabble, but specifically adapted to the game Towers of Babble by Everybody House Games. As the game explains the game uses a variant of the US Scrabble Dictionary, so to match the games dictionary I extracted the words directly from the game files. The normal Towers, Mods and Harvesters are all located in a file called units.json placed inside the TowersOfBabble_Data\StreamingAssets. The cursed words were harder to find, as they are only listed in a document called cursed_words.txt without any stats. I had an AI extract the data and make a json file with the stats. Most of the program was written with AI, only fine-tuning, correction and styling was done by me.

### The program has the following features:
- Find words by available letters
- Find words starting or / and ending with specific letters
- Find words containing specific letters, in order or out of order and with specific amount
- Combine any of the above
- Sort words by stats, type, group and filter
- Save favorite words and find them easily

## Compiling
In releases you will find a zip file containing an exe, but if you would like to compile it yourself you are welcome to do so. I compiled it using PyInstaller with the following command:
```
py -m PyInstaller --onefile --windowed --icon=icon.ico TowersOfBabbleWordFinder.py
```

## Open Source
This is my first time publishing a repository publically and I am still in the process of learning. If you see anything wrong you are welcome to suggest/edit. I want this to be open source and I am very open to new features and bug fixes. The only thing is that I want it to match my design goals for the program, which are:
- Runs locally and does not connect to the internet, with the exception of an (optional) dictionary definition of words upon requesting it. (currently a button that opens a link, though I want to look into a different approach.)
- Simple to use, but not lacking in ability to do advanced searches.
- Functional code. I do not mind code being written by AI, as long as it works and does not slow the program down or make it unusable. This is not a big or important project and is just something I personally wanted while playing the game. Though if it can be beneficial to other people, great!
