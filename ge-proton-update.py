#!/bin/python3

import requests
import json
import tarfile 
import os

def update_proton():
    #get the latest release 
    ge_latest = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
    response = requests.get(ge_latest, verify=True)
    if response.status_code == 200:
        releases = response.json()
        #TODO add a if statement here that looks at releases -> assets -> name and then exits if we already exists in steamtools dir 
        return(releases['assets'][1]['browser_download_url'],releases['assets'][1]['name'])
    else:
        print("Failed reading GitHub API")

def check_exists(filepath):
    return os.path.isfile(filepath)

def parse_file_path(filename, downloaddir): 
    return downloaddir + filename 

def download_file(url, filepath):
    response = requests.get(url, stream=True)
    with open(filepath, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:  
                file.write(chunk)
    file.close()
    return(filepath)

def untar(filename, steamtools):
    if tarfile.is_tarfile(filename):
        with tarfile.open(filename, 'r:gz') as tar:
            tar.extractall(path=steamtools)  

def config(home_dir, config_dir, config_file_path):
    # Get user input
    print(f"NOTE: Give the absolute path, not just Downloads or .steam")
    download_path = input("Where is your downloads directory located: ")
    steamtools_path = input("Where is your compatibilitytools.d directory located: ")
    
    #Create a place to save the config json
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".config", "ge-proton-update")
    os.makedirs(config_dir, exist_ok=True)
    config_file_path = os.path.join(config_dir, "config.json")

    config_data = {
            "configured": True,
            "downloaddir": download_path,
            "steamtools": steamtools_path
    }
    
    with open(config_file_path, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

    print(f"Config saved to {config_file_path}")

def check_config(config_file_path):
    if os.path.exists(config_file_path):
        with open(config_file_path, "r") as config_file:
            config_data = json.load(config_file)
        if config_data.get("configured") is True:
            return (True, config_data.get("downloaddir"), config_data.get("steamtools"))
        else:
            config()

def main():
    
    home_dir = os.path.expanduser("~")
    config_dir = os.path.join(home_dir, ".config", "ge-proton-update")
    config_file_path = os.path.join(config_dir, "config.json") 
    logfile = "/var/log/ge-proton-update.log"
    
    configured = check_config(config_file_path)
    
    if configured is None :
        config(home_dir,config_dir,config_file_path)
    else:
        downloaddir = configured[1]
        steamtools = configured[2]
        x, y = update_proton()
        filepath = parse_file_path(y, downloaddir)
        if not check_exists(filepath): 
            file = download_file(x,filepath)
            untar(file, steamtools)
            exit(0)
        else:
            print(filepath + " already exists")
            exit(0)

if __name__ == "__main__":
    main()
