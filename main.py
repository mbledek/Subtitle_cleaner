import os
import re
from tkinter.filedialog import askopenfilename, askdirectory
import json
import subprocess

import pathlib
from logzero import logger, logfile

directory = pathlib.Path(__file__).parent.absolute()
logfile(str(directory) + "\\Subtitles.log")

pat = r'(?<=\[).+?(?=\])'

# Make sure the trash_list.txt is created and loaded
if not os.path.isfile("trash_list.txt"):
    with open("trash_list.txt", "w", encoding="utf-8") as f:
        f.write("")
    trash_list = []
else:
    with open("trash_list.txt", "r", encoding="utf-8") as f:
        trash_list = f.read().split("\n")


def extract_subtitles(file):
    # Get a list of streams in a file
    ffprobe_cmd = ["ffprobe.exe", "-hide_banner", "-show_streams", "-print_format", "json", file]
    process = subprocess.Popen(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = json.loads(process.communicate()[0])

    # Extract non-forced English subtitles
    for stream in output["streams"]:
        # print(stream)
        if stream["codec_type"] == "subtitle" and stream["tags"]["language"] == "eng":
            if "forced" in stream["tags"]["title"].lower():
                pass
            else:
                os.system(f'ffmpeg.exe -i {file} -map "0:{output["streams"].index(stream)}" {file}.srt')


def clean_subtitles(file):
    # Read the file with subtitles
    with open(file, "r", encoding="utf-8") as f:
        subtitles = f.read()

    # Find all occurrences of text inside ( )
    found = re.findall(pat, subtitles)

    # Delete those occurrences from subtitless
    for i in range(len(found)):
        if found[i].lower() in trash_list:
            subtitles = subtitles.replace(f"({found[i]})", "")
        else:
            print(found[i])
            # if input(":").lower() == "y":
            subtitles = subtitles.replace(f"({found[i]})", "")
            trash_list.append(found[i].lower())

    # Update the list of deleted text
    with open("trash_list.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(trash_list))

    # Update the subtitles
    with open(f"{file}", "w", encoding="utf-8") as f:
        f.write(subtitles)


def main():
    q = input("Directory (D) or File (F)? : ")
    if q.lower() == "d":
        # Get movies inside chosen directory
        folder = askdirectory()
        files_movies = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        for i in range(len(files_movies)):
            if files_movies[i][-4:] in [".mkv", ".mp4"]:
                # If subtitles already there, clean them
                if os.path.isfile(f"{folder}/{files_movies[i][:-4]}.srt"):
                    clean_subtitles(f"{folder}/{files_movies[i][:-4]}.srt")
                # If not, extract, then clean
                elif not os.path.isfile(f"{folder}/{files_movies[i]}.srt"):
                    extract_subtitles(f"{folder}/{files_movies[i]}")
                    try:
                        # Clean the subtitles
                        clean_subtitles(f"{folder}/{files_movies[i]}.srt")
                    except FileNotFoundError:
                        # If no subtitles were extracted, raise an error
                        logger.error("No subtitles found")
    elif q.lower() == "f":
        # Get the chosen file
        filename = askopenfilename()
        if filename[-4:] in [".mkv", ".mp4"]:
            # Check for existing subtitles
            if not os.path.isfile(f"{filename}.srt"):
                extract_subtitles(filename)
            # Clean the subtitles
            clean_subtitles(f"{filename}.srt")
        elif filename[-4:] in [".txt", ".srt"]:
            # Clean the subtitles
            clean_subtitles(f"{filename}")


if __name__ == "__main__":
    main()
