import os.path

def empty_dir(path):
    for file in os.listdir(path):
        if os.path.isdir((newpath := os.path.join(path, file))):
            empty_dir(newpath)
            os.rmdir(newpath)
        else:
            os.remove(newpath)