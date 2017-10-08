import os
import sys
import json
import subprocess

def main():
    try:
        with open("config.json", "r") as c:
            config = json.load(c)
            c.close()
    except FileNotFoundError:
        print("config.json not found. Check to make sure all files are in your current directory, then try running the program again.")
        sys.exit()
        
    try:
        installPath = config["mugen-install"]
        emptySlot = config["empty-space"] + "\n"
    except KeyError as err:
        print("\"{}\" was missing from your confg.json. Please double-check, then try running the program again.")
        sys.exit()
        
    selectDef = []
    try:
        print(os.path.join(installPath, "data", "select.def"))
        sd = open(os.path.join(installPath, "data", "select.def"), "r")
        
        for line in sd.readlines():
            selectDef.append(line)
        sd.close()
    except FileNotFoundError:
        print("\"select.def\" could not be found in your MUGEN install directory. Please double-check that all files are in your \"data\" folder, then try running the program again.")
        sys.exit()
        
    charList = []
    stageList = []
    
    insIndex = 0
    lnIndex = 0
    
    installedChars = 0
        
    try:
        charList = os.listdir(os.path.join(".", "install", "chars"))
    except FileNotFoundError:
        os.mkdir(os.path.join(".", "install", "chars"))
        
    # install characters first
    for char in charList:
        foundAnEmptySlot = False
        lnIndex = 0

        for line in selectDef:
            if line == emptySlot:
                print("found an empty slot")
                foundAnEmptySlot = True
                break
            lnIndex += 1
            
        if not foundAnEmptySlot:
            print("It seems that there are no more empty slots in your \"select.def\". More characters cannot be added.")
            break
                
        sys.stdout.write("Installing {}...    ".format(char))
        
        # TODO: add zip file support
        try:
            with open(os.path.join("install", "chars", char, "{}.json".format(char)), "r") as cc:
                charConfig = json.load(cc)
                charLine = charConfig["line"]
                cc.close()
        except FileNotFoundError:
            charLine = char
            
        os.rename(os.path.join("install", "chars", char), os.path.join(installPath, "chars", char))
        if not charLine.endswith("\n"):
            selectDef[lnIndex] = charLine + "\n"
        else:
            selectDef[lnIndex] = charLine
        
        sys.stdout.write("Done.\n")
        installedChars += 1
    
    sys.stdout.write("Writing to \"select.def\"...   ")
    
    lnIndex = 0
    with open(os.path.join(installPath, "data", "select.def"), "w+") as sd:
        for line in selectDef:
            sd.write(line)
        sd.close()
        
    sys.stdout.write("Done.\n")
    print("{} characters installed successfully.".format(installedChars))
    print("Now running MUGEN...")
    
    # thanks:  https://stackoverflow.com/questions/21406887/subprocess-changing-directory
    subprocess.Popen("cd {} && .\\mugen.exe".format(installPath), shell = True)
    sys.exit()
    
if __name__ == "__main__":
    main()