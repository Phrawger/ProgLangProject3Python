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

def dirinfoget(a_path): #finds and returns applicable information about the given directory
    pathinfo = [0, 0, 0, 0, 0]
    
    #add the given path to our two lists of information, so that subdirectories are listed after their parents
    checkeddirs.append(a_path)
    dirinfo[a_path] = pathinfo
    
    pathdirs = os.listdir(a_path)
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
    dirinfo[a_path] = pathinfo
    return pathinfo
    
def fileinfoget(a_file): #finds and returns applicable information about the given .java file
    fileinfo = [0, 0, 0, 0, 0]
    commented = false
    
    fileinfo[0] = os.stats(a_file).st_size
    
    f = open(a_file)
    file_lines = [line.strip('\n') for line in f]
    f.close()
    
    for line in file_lines:
        line = line.split()
        for word in line:
            if not commented:
                if re.match("//+",word): break
                elif re.match("/\\*+", word): commented = true
                elif word == "public": fileinfo[1] += 1
                elif word == "private": fileinfo[2] += 1
                elif word == "try": fileinfo[3] += 1
                elif word == "catch": fileinfo[4] += 1
            else:
                if re.match("*\\*/",word): commented = false
    return fileinfo

runthis = dirinfoget(srcpath)
for check in checkeddirs:
    print check + "\t" + dirinfo[check][0] + " bytes\t" + dirinfo[check][1] + " public\t" + dirinfo[check][2] + " private\t" + dirinfo[check][3] + " try\t" + dirinfo[check][4] + " catch\n"