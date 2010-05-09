#!/usr/bin/python

"""
Copy Robot

If it detects that a disc has been inserted in the dvd drive, then 
copy all of the disc contents to a target directory. Once finished
copying, it will eject the disc, and wait for a new disc to be inserted.

This script is handy for those who wish to copy all of their
CD and DVD contents to an external hard drive, which will
help contribute to eliminate physical media.


       Author : Kelvin Ng (deepblade@gmail.com)
      Created : May 8th, 2010
  Environment : Mac OSX
        Notes : I use the term 'discs' as to refer to both CDs and DVDs
"""

import os
import re
import time
import shutil

# The directory where we want to copy all the contents to
targetDir = "/Volumes/1.5 Terabyte/temp/"

# Returns the mount point of the DVD drive, if a disc is inserted.
# If no disc is inserted, it will return None
def get_DVD_mount():
	
	# Get the device of the DVD drive 
	getDevice_cmd = "mount | grep -i read-only | grep -i cd | cut -d\" \" -f1"
	device = runShell(getDevice_cmd)
	
	# There is no disc in the drive! There's no point in
	# looking up the mount point for the device
	if len(device) == 0:
		return None
	
	# Lookup the mount point for the device
	cmd = "df | grep " + device
	output = runShell(cmd)
	
	# Match this pattern, to get the volume mount ("/Volumes/My Disc"):
	# /dev/disk1s2     8974784    8974784         0   100%    /Volumes/My Disc
	p = re.compile("^(.+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+\%)\s+(.+)$")
	m = p.match(output)
	
	# If we didn't find the pattern, then something went wrong
	# and it probably means there's no disc
	if (m == None) or (len(m.group()) < 6):
		# No disc in DVD drive
		return None
	else:
		# Return the mount point
		return m.group(6)



# This function runs a command in the shell and then returns the output
def runShell(cmd):
	stdout_handle = os.popen(cmd)
	stdout_output = stdout_handle.read()
	stdout_output = stdout_output.rstrip()
	
	return stdout_output


# Main
def main():
	
	# Keep track of the number of discs we've copied
	discCount = 0
	
	while True:
		
		# Increment the disc counter
		discCount = discCount + 1
		
		# A flag to represent whether we've displayed the "waiting for disc"
		# message or not. If we have, then there's no need to display it
		# over and over again as "wait" loop keeps looping
		displayMsgAlready = False
	
		# Get the DVD drive mount point
		DVD_drive = get_DVD_mount()
	
		# While no disc has been inserted in the DVD drive yet,
		# then keep sleeping and waiting for a disc to be inserted
		while (DVD_drive == None):
			if (displayMsgAlready == False):
				print "No disc inserted. Please insert a disc"
				displayMsgAlready = True
			
			time.sleep(1)
		
			# Try reading the drive again
			DVD_drive = get_DVD_mount()
		
		
		# A disc was inserted! We're no longer waiting.
		# Copy the disc contents to the target directory
		
		# Create a new directory in the target directory: 
		# eg. /Volumes/externalHD/1
		cur_TargetDir = targetDir + "/" + str(discCount)
		
		print "Copying contents of " + DVD_drive + " to " + cur_TargetDir
		shutil.copytree(DVD_drive, cur_TargetDir)
		
		
		# Once we're done, eject the disc
		print "Ejecting disc..."
		runShell("drutil eject")
		print "-----------------------------------"
		
		time.sleep(1)
		
		# Start the loop again
		continue
		
# Main
if __name__ == "__main__":
    main()
