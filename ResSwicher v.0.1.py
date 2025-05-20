import json
import os
import win32api
import win32con
from pathlib import Path

USER_PROFILE = os.path.expanduser("~")
CONFIG_FILE = os.path.join(USER_PROFILE, "resolutions.json")

def load_resolutions():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {e}")
    return None

def save_resolutions(resolutions):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(resolutions, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving config file: {e}")

def input_resolution(prompt):
    while True:
        try:
            res_input = input(prompt).strip()
            if res_input.lower() == 'stop':
                return None
                
            parts = res_input.split()
            if len(parts) < 2:
                raise ValueError("Please enter both resolution and refresh rate")
                
            resolution = parts[0]
            if 'x' not in resolution:
                raise ValueError("Resolution must be in WIDTHxHEIGHT format")
                
            width, height = map(int, resolution.split('x'))
            freq = int(parts[1])
            
            return {
                'width': width,
                'height': height,
                'freq': freq,
                'name': f"{width}x{height} {freq}Hz"
            }
        except ValueError as e:
            print(f"Error: {e}. Please try again or type 'stop'")

def setup_resolutions():
    print("\n=== Resolution Setup ===")
    print("You need to add at least 2 resolutions")
    print("\033[31mWARNING: IF YOU DON'T KNOW YOUR FREQUENCY TYPE 60\033[0m")
    print("\033[31mWARNING: YOUR CUSTOM RESOLUTION MUST BE IN NVIDIA OR AMD SOFTWARE OTHERWISE RESOLUTION WILL NOT BE CHANGED\033[0m") 
    print("Format: WIDTHxHEIGHT FREQUENCY (e.g.: 1920x1080 144)")
    print("Type 'stop' to finish (after minimum 2 resolutions)")
    
    resolutions = []
    while len(resolutions) < 2:
        res = input_resolution(f"Resolution {len(resolutions)+1}: ")
        if not res:
            if len(resolutions) >= 2:
                break
            print("You need to add at least 2 resolutions!")
            continue
        resolutions.append(res)
    
    # Add additional resolutions (up to 5)
    for i in range(len(resolutions), 5):
        res = input_resolution(f"Resolution {i+1} (additional, type 'stop' to finish): ")
        if not res:
            break
        resolutions.append(res)
    
    save_resolutions(resolutions)
    print(f"\nResolutions saved to: {CONFIG_FILE}")
    return resolutions

def add_resolution(resolutions):
    print("\n=== Add New Resolution ===")
    new_res = input_resolution("Enter new resolution (format: WIDTHxHEIGHT FREQUENCY): ")
    if new_res:
        resolutions.append(new_res)
        save_resolutions(resolutions)
        print(f"✅ Resolution {new_res['name']} added successfully!")
        print(f"Config file: {CONFIG_FILE}")
    return resolutions

def change_resolution(width, height, freq):
    devmode = win32api.EnumDisplaySettings(None, win32con.ENUM_CURRENT_SETTINGS)
    devmode.PelsWidth = width
    devmode.PelsHeight = height
    devmode.DisplayFrequency = freq
    devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT | win32con.DM_DISPLAYFREQUENCY
    
    try:
        win32api.ChangeDisplaySettings(devmode, win32con.CDS_UPDATEREGISTRY)
        print(f"✅ Resolution changed to {width}x{height} {freq}Hz")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print(f"\033[33mConfiguration file will be saved to: {CONFIG_FILE}\033[0m")
    
    resolutions = load_resolutions()
    
    if not resolutions:
        resolutions = setup_resolutions()
        if not resolutions:
            print("Not enough resolutions added. Program terminated.")
            return
    
    while True:
        print("\n=== Available Resolutions ===")
        for i, res in enumerate(resolutions, 1):
            print(f"{i} - {res['name']}")
        print("a - Add new resolution")
        print("0 - Exit")
        
        choice = input("Select action: ").strip().lower()
        
        if choice == '0':
            break
        elif choice == 'a':
            resolutions = add_resolution(resolutions)
        elif choice.isdigit():
            choice_num = int(choice)
            if 1 <= choice_num <= len(resolutions):
                res = resolutions[choice_num-1]
                change_resolution(res['width'], res['height'], res['freq'])
            else:
                print("❌ Invalid resolution number")
        else:
            print("❌ Invalid input")

if __name__ == "__main__":
    main()