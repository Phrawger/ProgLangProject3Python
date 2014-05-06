import os
import re
import sys


#sys.argv[1] contains the diretory submitted by the user, this value is then stored in the variable srcpath
#os.chroot changes the root of the process to the path given by the user
srcpath = sys.argv[1]
os.chroot(srcpath)

#checkeddirs holds a list of the directories that have already been checked for word counts and file sizes
checkeddirs = []

#dirinfo is a dictionary with keys taken from checkeddirs and values which are lists of the recorded traits of each of those directories
#each entry in dirinfo is of the following form:
#directory path : [combined size of all java files in bytes, # of instances of 'public', # of instances of 'private', # of instances of 'try', # of instances of 'catch']
dirinfo = {}

#fileinfoget: takes a file path, assumed to be that of a java file (string), returns file info (5 element list)
def fileinfoget(a_file):
    #set default output to add values to
    fileinfo = [0, 0, 0, 0, 0]
    #define the variable for whether or not the code is commented out
    commented = false
    
    #get the size of the file in bytes and save it in the fileinfo list
    fileinfo[0] = os.stats(a_file).st_size
    
    #grab all of the lines of text from the file and put them in a list, removing the newline characters from the ends of each line
    f = open(a_file)
    file_lines = [line.strip('\n') for line in f]
    f.close()
    
    #for each line in the list of lines
    for line in file_lines:
        line = line.split()
        for word in line:
            #if the code is not being commented out
            if not commented:
                #skip the rest of the line if a line comment appears
                if re.match("//+",word): break
                #if a block comment begins, set commented to true
                elif re.match("/\\*+", word): commented = true
                #if it's a word we're looking for, update the fileinfo accordingly
                elif word == "public": fileinfo[1] += 1
                elif word == "private": fileinfo[2] += 1
                elif word == "try": fileinfo[3] += 1
                elif word == "catch": fileinfo[4] += 1
            #check for commented in case a block comment is used like /*this*/
            if commented:
                if re.match("*\\*/",word): commented = false
    #return the updated information
    return fileinfo

#dirinfoget: takes a file path (string), returns directory info (5 element list)
def dirinfoget(a_path): 
    #set default output to add values to
    pathinfo = [0, 0, 0, 0, 0]
    
    #add the given path to our two lists of information, so that subdirectories are listed after their parents
    checkeddirs.append(a_path)
    dirinfo[a_path] = pathinfo
    
    #store the list of files and folders within this directory
    pathdirs = os.listdir(a_path)
    #for each file or folder in the list:
    for adir in pathdirs:
        if re.match("*\\.java",adir):
            #if it's a java file, get its info and add it to the info for this directory
            javainfo = fileinfoget(a_path + adir)
            for i in range(0,5):
                pathinfo[i] = pathinfo[i] + javainfo[i]
            
        elif not os.listdir(a_path + adir + "/"):
            #if it's another directory with more files or folders, recurse and then add the returned info to this directory's info
            innerinfo = dirinfoget(a_path + adir + "/")
            for i in range(0,5):
                pathinfo[i] = pathinfo[i] + innerinfo[i]
    #update the dirinfo listing for this directory
    dirinfo[a_path] = pathinfo
    return pathinfo

#run dirinfoget on the source directory, and it will recurse through all the directories below it
runthis = dirinfoget(srcpath)
#print out each of the directories we searched through
for check in checkeddirs:
    print check + "\t" + dirinfo[check][0] + " bytes\t" + dirinfo[check][1] + " public\t" + dirinfo[check][2] + " private\t" + dirinfo[check][3] + " try\t" + dirinfo[check][4] + " catch\n"