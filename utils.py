import os.path

def empty_dir(self, path):
    for file in os.listdir(path):
        if os.path.isdir((newpath := os.path.join(path, file))):
            self.empty_dir(newpath)
            os.rmdir(newpath)
        else:
            os.remove(newpath)