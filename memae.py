import os
import sys
import json
import subprocess
import zipfile

# I come up with the most creative names, don't I
def getSlashIndex(path):
    cIndex = 0
    for char in path:
        if char == "/":
            return cIndex
            
        cIndex += 1
            
    return -1

def main():
    if not os.path.exists("install"):
        os.mkdir("install")

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
    failedChars = 0
        
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
        
        basename = char
        try:
            jsPath = os.path.join("install", "chars", char, "memae.json")
            with open(jsPath) as cc:
                charConfig = json.load(cc)
                charLine = charConfig["line"]
                cc.close()
        except FileNotFoundError:
            sys.stdout.write("JSON File not found...  ")
            charLine = char
            
        if char.endswith(".zip"):
            basename = char[:len(char) - 4]
            z = zipfile.ZipFile(os.path.join("install", "chars", char))
            extractToDirectory = True
            print(z.namelist())
            for entry in z.namelist():
                if '{}.def'.format(basename) in entry and "/" in entry:   # the .def file is stored in a subdirectory
                    extractToDirectory = False
                    path = os.path.join("install", "chars")
                    break
                    
            charLine = basename
            for entry in z.namelist():
                if "memae.json" in entry:
                    js = z.read(entry)
                    js = js.decode("utf-8")
                    print(js)
                    jsData = json.loads(js)
                    charLine = jsData["line"]
                    
            if extractToDirectory:
                os.mkdir(os.path.join("install", "chars", basename))
                path = os.path.join("install", "chars", basename)
                
            z.extractall(path = path)
            z.close()
            
        try:
            os.rename(os.path.join("install", "chars", basename), os.path.join(installPath, "chars", basename))
        except FileExistsError:
            print("File already exists, skipping...")
            failedChars += 1
            continue
        if not charLine.endswith("\n"):
            selectDef[lnIndex] = charLine + "\n"
        else:
            selectDef[lnIndex] = charLine
        
        sys.stdout.write("Done.\n")
        installedChars += 1
    0
    sys.stdout.write("Writing to \"select.def\"...   ")
    
    lnIndex = 0
    with open(os.path.join(installPath, "data", "select.def"), "w+") as sd:
        for line in selectDef:
            sd.write(line)
        sd.close()
        
    sys.stdout.write("Done.\n")
    print("\n\n--------------------------------")
    print("|           RESULTS            |")
    print("--------------------------------")
    print("{} characters installed successfully.".format(installedChars))
    print("{} failed character installations.".format(failedChars))
    print("Now running MUGEN...")
    
    # thanks:  https://stackoverflow.com/questions/21406887/subprocess-changing-directory
    #subprocess.Popen("cd {} && .\\mugen.exe".format(installPath), shell = True)
    sys.exit()
    
if __name__ == "__main__":
    main()