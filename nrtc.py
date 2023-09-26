#!/usr/bin/env python3
#
#  nrtc.py
#
#  Copyright 2023 Curtis Lee Bolin <CurtisLeeBolin@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import datetime
import os
import re
import subprocess
import time
import avtc


class NRTC(avtc.AVTC):

    def transcode(self, file, fileName, crop, deinterlace, transcodeForce):
        inputFile = f'{self.inputDir}/{file}'
        outputFile = f'{self.outputDir}/{fileName}.mp4'
        outputFilePart = f'{outputFile}.part'
        errorFile = f'{outputFile}.error'

        if not os.path.isfile(f'{file}.lock'):
            with open(f'{file}.lock', 'w') as f:
                pass

            print(f'{self.workingDir}/{file}')

            transcodeArgs = [
              'ffmpeg', '-i', file, '-filter:v',
              'scale=w=\'max(1920,iw)\':h=\'min(1080,ih)\':force_original_aspect_ratio=decrease:force_divisible_by=8',
              '-c:v', 'libx265', '-c:a', 'aac', '-movflags', '+faststart',
              '-map_metadata', '-1', '-y', '-f', 'mp4',
              outputFilePart]
            returncode, stderrList = self.runSubprocess(transcodeArgs)
            if returncode == 0:
                os.remove(f'{file}.lock')
                os.rename(file, inputFile)
                os.rename(outputFilePart, outputFile)
            else:
                self.writeErrorFile(errorFile, transcodeArgs, stderrList)
            return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        prog='nrtc.py',
        description='NR Video TransCoder',
        epilog=(
            'Copyright 2023 Curtis Lee Bolin <CurtisLeeBolin@gmail.com>'))
    parser.add_argument(
        '-d', '--directory', dest='directory', help='A directory')
    parser.add_argument(
        '-f', '--filelist', dest='fileList', help=(
            'A comma separated list of files in the current directory'))
    args = parser.parse_args()

    if (args.fileList and args.directory):
        print(
            'Arguments -f (--filelist) and -d (--directory) can not be ',
            'used together')
        exit(1)
    elif (args.fileList):
        workingDir = os.getcwd()
        fileList = args.fileList.split(',')
    elif (args.directory):
        workingDir = args.directory
        fileList = os.listdir(workingDir)
        fileList.sort()
    else:
        workingDir = os.getcwd()
        fileList = os.listdir(workingDir)
        fileList.sort()

    tc = NRTC(workingDir, fileList)
    tc.run()


if __name__ == '__main__':
    main()
