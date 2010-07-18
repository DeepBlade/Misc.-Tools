#!/usr/bin/python

import os
import re
import time
import shutil

# The directory where we want to copy all the contents to
targetDir = "/Volumes/Drobo/temp/"





"""
 If a disc is inserted in the drive, this function
 returns 3 items about the disc drive:
 	- the device path (eg. "/dev/disk3")
 	- the mounted volume path (eg. "/Volumes/TERMINATOR")
 	- the name of the volume (eg. "TERMINATOR")

 If no disc is inserted, it will return (None,None,None)
"""
def getDiscDriveInfo():
	
	# Get the device of the DVD drive 
	getDevice_cmd = "drutil status | grep Name | cut -d:  -f3"
	discDevice = runShell(getDevice_cmd)
	
	# whitespace removal
	discDevice = discDevice.strip()
	
	# If there is no disc in the drive, then
	# there's no point in proceeding
	if (discDevice == ""):
		return (None, None, None)
	
	# Else, proceed and look up the mount point for the device
	cmd = "df | grep " + discDevice
	dfOutput = runShell(cmd)
	
	# Match this pattern:
	# "/dev/disk1s2     8974784    8974784         0   100%    /Volumes/TERMINATOR"
	#      (1)           (2)        (3)          (4)   (5)         (6)
	p = re.compile("^(.+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.+\%)\s+(.+)$")
	m = p.match(dfOutput)
	
	# If we didn't find the pattern, then something went wrong
	# and it probably means there's no disc
	if (m == None) or (len(m.group()) < 6):
		# No disc in DVD drive
		return (None, None, None)
	
	# Else, proceed and return the 3 strings
	discDevice = m.group(1) # redundant, but whatever
	discVolumePath = m.group(6)
	discVolumeName = runShell("diskutil list "+ discDevice +" | tail -1 | awk {'print $2'}")
		
	return (discDevice, discVolumePath, discVolumeName)



"""
This function runs a command in the shell and then returns the output
"""
def runShell(cmd):
	stdout_handle = os.popen(cmd)
	stdout_output = stdout_handle.read()
	stdout_output = stdout_output.rstrip()
	
	return stdout_output


# Main
def main():
	
	# Keep track of the number of discs we've copied
	discCount = 0
	
	# This script runs indefinitely, until you hit ctrl + c to kill it
	while True:
		
		# Increment the disc counter
		discCount = discCount + 1
		
		# A flag to represent whether we've displayed the "waiting for disc"
		# message or not. If we have, then there's no need to display it
		# over and over again as "wait" loop keeps looping
		displayMsgAlready = False
	
		# Get the DVD drive mount point
		(discDevice, discVolumePath, dvdVolumeName) = getDiscDriveInfo()
	
		# While no disc has been inserted in the DVD drive yet,
		# then keep sleeping and waiting for a disc to be inserted
		while (discVolumePath == None):
			if (displayMsgAlready == False):
				print "No disc inserted. Please insert a disc"
				displayMsgAlready = True
			
			time.sleep(1)
		
			# Try reading the drive again
			(discDevice, discVolumePath, dvdVolumeName) = getDiscDriveInfo()
		
		
		# A disc was inserted! We're no longer waiting.
		# Copy the disc contents to the target directory
		
		# Create a new directory in the target directory: 
		# eg. /Volumes/externalHD/1
		cur_TargetDir = targetDir + "/"

		# The full target path would be, for example:
		# /Volumes/Drobo/temp/TERMINATOR.iso
		fullTargetPath = cur_TargetDir+ dvdVolumeName + ".iso"
		
		print "Imaging " + discVolumePath + " to " + fullTargetPath
		#shutil.copytree(DVD_drive, cur_TargetDir)
		
		# unmount (but not eject) the drive
		runShell("diskutil unmountDisk " + discDevice)
		runShell("dd if=" + discDevice + " of="+ fullTargetPath + " bs=2048")
		
		
		
		
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