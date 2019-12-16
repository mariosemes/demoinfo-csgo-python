#!/usr/bin/env python3.8

#sudo apt install protobuf-compiler

from os import path, mkdir, rmdir
import subprocess
from shutil import rmtree

import glob

IMPORT_FOLDER = path.join('protobufs')
OUTPUT_FOLDER = path.join('demoinfocsgo/proto')

def make_python_imported_folder(folder):
    mkdir(folder)
    with open(path.join(folder, '__init__.py'), 'w') as f:
        pass


# TODO: for some reason MSG_SPLITSCREEN_TYPE_BITS is switched from 1 to 2, need to check if its needed
def convert_folder(subfolder):
    input_folder = path.join(IMPORT_FOLDER, subfolder)
    output_folder = path.join(OUTPUT_FOLDER, subfolder)
    make_python_imported_folder(output_folder)

    for file in glob.glob(input_folder + '/**/*.proto', recursive=True):
        output_file = file + '.py'
        print(f'Converting {file} to {output_file}')
        subprocess.call(["protoc", f'--proto_path={input_folder}', f'--proto_path={IMPORT_FOLDER}', f'--python_out={output_folder}', file])

def main():
    try:
        rmtree(OUTPUT_FOLDER)
    except:
        pass

    make_python_imported_folder(OUTPUT_FOLDER)
    convert_folder('csgo')
    convert_folder('google')

if __name__ == '__main__':
    main()