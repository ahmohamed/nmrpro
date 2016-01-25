from os.path import isfile, isdir, basename, exists, join
from os import walk
from tarfile import open
import tempfile
from fnmatch import filter
#import re
temp = tempfile.gettempdir()

def get_files(filepath):  
    # if the input is a file, then it may be a tar, NMRPipe or ucsf file
    if isfile(filepath):        
        if filepath.endswith((".tar.gz",".tar")):
            if(filepath.endswith(".tar")): filebasename = basename(filepath)[:-4]
            else: filebasename = basename(filepath)[:-7]
            
            temp_dir = join(temp, filebasename)
            if not exists(temp_dir):
                tar = open(filepath)
                tar.extractall(path=temp_dir)
                tar.close()
            
            return get_files(temp_dir)
            
        
        if filepath.endswith((".ft", ".ft2", ".fid")):
            return [(filepath, 'Pipe')]
        
        if filepath.endswith(".ucsf"):
            return [(filepath, 'Sparky')]
            
    elif isdir(filepath):
        files = []
        for root, dirnames, filenames in walk(filepath):
            for filename in filter(filenames, "acqu*"):
                if (root, "Bruker") not in files: files.append((root,"Bruker"))
            for filename in filter(filenames, "*.ft*"):
                if ( join(root, filename), "Pipe") not in files: files.append( ( join(root, filename),"Pipe") )
            for filename in filter(filenames, "*.ucsf"):
                if (join(root, filename), "Sparky") not in files: files.append( (join(root, filename),"Sparky") )
        
        if len(files) > 0: return files
                    
    #return [(filepath, 'None')]
    return None

def find_pdata(filepath, ndim):
    pdata_name = {
        1:'1r',
        2:'2rr'
    }[ndim]
    
    for root, dirnames, filenames in walk(filepath):
        if len(filter(filenames, pdata_name)) > 0:
            return root
    return None