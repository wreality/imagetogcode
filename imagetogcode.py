#!/usr/bin/python
#
#    imagetogcode
#    Copyright 2013 Brian Adams
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

"""Convert an image file to gcode a Marlin powered laser cutter can understand"""
import sys, getopt

import Image
import ImageOps

import base64

def imagetogcode(image, f):
    
    img = ImageOps.invert(image)
    width, height = img.size

    f.write("; Image pixel size: "+str(width)+"x"+str(height)+"\n");

    pixels = list(img.getdata())
    pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
    forward = True

    def get_chunks(arr, chunk_size = 51):
        chunks  = [ arr[start:start+chunk_size] for start in range(0, len(arr), chunk_size)]
        return chunks
    
    for row in reversed(pixels):
        if not forward:
            f.write("G8 ")
            result_row = row[::-1]
        else:
            result_row = row
            f.write ( "G7 ");
        forward = not forward
        first = True
        
        for chunk in get_chunks(result_row):
            if not first:
                f.write("G9 ")
            else:
                first = not first
            b64 = base64.b64encode("".join(chr(x) for x in chunk))
            f.write("L"+str(len(b64))+" ")
            f.write("D"+b64+ "\n")
            

def main(argv):
    inputfile = None
    
    def showhelp():
        print "imagetogcode: Process an input image to gcode for a Marlin laser cutter."
        print
        print "Usage: imagetogcode -i <input file> -o [output file]"
    
    outputfile = None
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["input=", "output="])
    except getopt.GetoptError:
        showhelp()    
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            showhelp()
            sys.exit()
        if opt in ('-i', '--input'):
            inputfile = arg
        elif opt in ('-o', '--output'):
            outputfile = arg
    if inputfile is None:
        showhelp()
        sys.exit(2)
    try:
        image = Image.open(inputfile).convert('L')
    except IOError:
        print "Unable to open image file."
        sys.exit(2)
    if outputfile is None:
        gcode = sys.stdout
    else:
        try:
            gcode = open(outputfile, "w")
        except IOError:
            print "Unable to open output file."
    
    imagetogcode(image, gcode)
    

if __name__ == "__main__":
    main(sys.argv[1:])
