from os.path import isfile, isdir, isabs, basename, exists, join
from os import walk, fdopen
import shutil
import tarfile
import tempfile
import zipfile
from fnmatch import filter
#import re
temp = tempfile.gettempdir()

def temp_save(data):
    ### write the data to a temp file
    filename = basename(data.name)
    handle, filepath = tempfile.mkstemp(suffix=filename) # make a tmp file
    f = fdopen(handle, 'w') # open the tmp file for writing
    f.write(data.read()) # write the tmp file
    f.close()
    
    print("temp_save", filename)
    return filepath

def get_file_path(fileobj):
    if isabs(fileobj.name) and exists(fileobj.name):
        return fileobj.name
    
    return temp_save(fileobj)

def get_files(_file):
    is_obj = False
    try:
        filename = basename(_file.name)
        is_obj = True
    except AttributeError:
        if not isinstance(_file, basestring):
            raise ValueError('_file should be either a string or a file-like object.')
        
        filename = basename(_file)
    
    print("_file", _file)
    # if the input is a file, then it may be a tar, NMRPipe or ucsf file
    if is_obj or isfile(_file):

        if filename.endswith((".tar.gz",".tar")):
            filebasename = filename.rstrip(".gz").rstrip(".tar")

            temp_dir = join(temp, filebasename)
            # TODO: this would overwrite extracted files.
            if exists(temp_dir):
                shutil.rmtree(temp_dir)

            if is_obj:
                tar = tarfile.open(fileobj=_file)
            else:
                tar = tarfile.open(_file)
            tar.extractall(path=temp_dir)
            tar.close()

            return get_files(temp_dir)

        if filename.endswith((".zip", ".gzip")):
            filebasename = filename.rstrip(".gzip").rstrip(".zip")

            temp_dir = join(temp, filebasename)
            # TODO: this would overwrite extracted files.
            if exists(temp_dir):
                shutil.rmtree(temp_dir)

            with zipfile.ZipFile(_file) as zip_object:
                zip_object.extractall(path=temp_dir)

            return get_files(temp_dir)

        if filename.endswith((".ft", ".ft2", ".fid")):
            if is_obj:
                filepath = get_file_path(_file)
                print("filepath", filepath)
            else:
                filepath = _file
                
            return [(filepath, 'Pipe')]

        if filename.endswith(".ucsf"):
            if is_obj:
                filepath = get_file_path(_file)
            else:
                filepath = _file
            
            return [(filepath, 'Sparky')]

    elif not is_obj and isdir(_file):
        files = []
        for root, dirnames, filenames in walk(_file):
            for filename in filter(filenames, "acqu*"):
                if (root, "Bruker") not in files: files.append((root,"Bruker"))
            for filename in filter(filenames, "*.ft*"):
                if ( join(root, filename), "Pipe") not in files: files.append( ( join(root, filename),"Pipe") )
            for filename in filter(filenames, "*.ucsf"):
                if (join(root, filename), "Sparky") not in files: files.append( (join(root, filename),"Sparky") )

        if len(files) > 0: return files

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