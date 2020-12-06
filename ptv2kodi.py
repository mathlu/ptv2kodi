#!/usr/bin/python3
import os
import re
import urllib.request
import json

from config import *


def isplaying():
    values = {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": "1"}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = json.dumps(values).encode("utf-8")

    try:
        req = urllib.request.Request(rpc_url, data, headers)
        with urllib.request.urlopen(req) as f:
            res = f.read()
        json_response = json.loads(res)
        if len(json_response['result']) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(e)


def updatelibrary():
    values = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    data = json.dumps(values).encode("utf-8")

    try:
        req = urllib.request.Request(rpc_url, data, headers)
        with urllib.request.urlopen(req) as f:
            f.read()
    except Exception as e:
        print(e)


def getepisode(name):
    match = re.search(r'E(\d{2})', name)
    return match.group(1)


def getseason(name):
    match = re.search(r'S(\d{2})', name)
    return match.group(1)


def getmovietitle(name):
    match = re.search(r'^[^\[]*', name)
    return match.group(0).strip()


def getmovieyear(name):
    match = re.search(r'\[(\d{4})', name)
    try:
        return match.group(1)
    except re.error:
        return None


def getgroupname(info):
    match = re.search(r'group-title=\"(' + series_group_regex + '|' + movies_group_regex + ')\s+([^\"]*)', info[0])
    try:
        return match.group(2)
    except Exception as e:
        return None


def sanitizefilename(filename):
    keepcharacters = (' ', '.', '_', '(', ')', '[', ']', ':', '-')
    if filename[-1] == '.':
        filename = filename[:-1]
    filename_stripslashes = filename.replace("/", ".")
    return "".join(c for c in filename_stripslashes if c.isalnum() or c in keepcharacters).rstrip()


def fetchseries(info):
    seriesname = info[1][:-8].strip()
    epname = info[1].strip()
    filename = rootdirectory + '/tvshows/' + getgroupname(info) + '/' + sanitizefilename(
        seriesname) + '/' + sanitizefilename(epname) + '.strm'
    if not os.path.exists(rootdirectory + '/tvshows/' + getgroupname(info)):
        os.mkdir(rootdirectory + '/tvshows/' + getgroupname(info))
        print('Created group dir :' + rootdirectory + '/tvshows/' + getgroupname(info))
    if not os.path.exists(rootdirectory + '/tvshows/' + getgroupname(info) + '/' + sanitizefilename(seriesname)):
        os.mkdir(rootdirectory + '/tvshows/' + getgroupname(info) + '/' + sanitizefilename(seriesname))
        print('Created show dir :' + rootdirectory + '/tvshows/' + getgroupname(info) + '/' + sanitizefilename(
            seriesname))
    if not os.path.exists(filename):
        streamfile = open(filename, "w+")
        streamfile.write(lines[1])
        print("strm file created: ", filename)


def fetchmovies(info):
    if getmovieyear(info[1]):
        moviewithyear = (getmovietitle(info[1]) + " (" + getmovieyear(info[1]) + ")")
        filename = rootdirectory + '/movies/' + getgroupname(info) + '/' + sanitizefilename(moviewithyear) + '.strm'
        if not os.path.exists(rootdirectory + '/movies/' + getgroupname(info)):
            os.mkdir(rootdirectory + '/movies/' + getgroupname(info))
            print('Created group dir :' + rootdirectory + '/movies/' + getgroupname(info))
        if not os.path.exists(filename):
            streamfile = open(filename, "w+")
            streamfile.write(lines[1])
            print("strm file created: ", filename)


if not os.path.exists(rootdirectory + '/movies'):
    os.mkdir(rootdirectory + '/movies')
    print('Created movie dir')

if not os.path.exists(rootdirectory + '/tvshows'):
    os.mkdir(rootdirectory + '/tvshows')
    print('Created tv dir')

with urllib.request.urlopen(url) as url:
    streamlist = url.read().decode('utf-8')
streams = streamlist.split("#EXTINF:-1")
del streams[0]
for i in range(len(streams)):
    stream = []
    lines = streams[i].split("\n")
    extinf = lines[0].split(",")
    if re.search(r'group-title=\"' + series_group_regex, extinf[0]):
        if getgroupname(extinf) in skipped_groups:
            continue
        fetchseries(extinf)
    if re.search(r'group-title=\"' + movies_group_regex, extinf[0]):
        if getgroupname(extinf) in skipped_groups:
            continue
        fetchmovies(extinf)
if not isplaying():
    updatelibrary()
