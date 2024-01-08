#! python
from glob import glob
import shutil
from pathlib import Path
import re
from posixpath import normpath
import re
import argparse
description = '''
This utility is used to transform directory paths or filenames by replacing certain patterns. It takes two positional arguments and one optional argument.

Positional arguments:
p1: The pattern in the existing file or directory paths. Use '#n' to represent a variable part of the path that will be replaced. Use '##n' to glob match multiple directories.
p2: The pattern for the new file or directory paths. Use '#n' to represent the part of the path that will be replaced by '#n' in p1.
'n' can be any singe digit integer
p2 can include formatting strings for integers (e.g. '%03d') which will be replaced by the index of the file or directory in the list of matches.


Optional arguments:
--move: If this argument is provided, the files or directories matching p1 will be moved to the new paths specified by p2. If this argument is not provided, the script will try to copy the files instead.

Examples:
1. To move a file to a nested directory:
python transform_dirs.py  "fil#1.txt" 'nested#1/fil.txt'

3. To move files from multiple directories to a single directory:
python transform_dirs.py  "##1/nested#1/fil.txt" 'out/fil#1.txt'

4. To move files from multiple directories to a single directory and rename them with a number:
python transform_dirs.py  "##1/nested#1/fil.txt" 'out/fil_%03d.txt'
'''
parser = argparse.ArgumentParser(description=description,formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('p1')
parser.add_argument('p2')
parser.add_argument('--move',action='store_true')
args = parser.parse_args()
num_tokens = 5
'''
# match part of file names
python ~/UtilityScripts/transform_dirs.py  "20bn-something-something-v2-#1.zip" "something/20bn-something-something-v2-#1.zip"
python ~/UtilityScripts/transform_dirs.py  "fil#1.txt" 'nested#1/fil.txt'

# glob match multiple directories with double hash
python ~/UtilityScripts/transform_dirs.py  "##1/nested#1/fil.txt" 'out/fil#1.txt'

# disambiguate files with file number
python ~/UtilityScripts/transform_dirs.py  "##1/nested#1/fil.txt" 'out/fil_%03d.txt'
'''
# p1 = '/data01/mc48/latent-diffusion/datasets/claw_data/full_frames/for_scale_2_frames_full/GH010058/raw/#1_mask.png'
# p2 = '/data01/mc48/latent-diffusion/datasets/claw_data/full_frames/for_scale_2_frames_full/GH010058/raw'
# p1 = "/Users/mc48/Desktop/20bn-something-something-v2-#1.zip"
# p2 = "~/Desktop/copy/#1/fil.zip"

# p1 = "/Users/mc48/Desktop/20bn-something-something-v2-#1.zip"
# p2 = "/Users/Desktop/something/20bn-something-something-v2-#1.zip"
def to_glob(pat):
    for n in range(num_tokens):
        pat = pat.replace(f'##{n}','**')
    for n in range(num_tokens):
        pat = pat.replace(f'#{n}','*')
    return pat

def to_regex(pat):
    for n in range(num_tokens):
        pat = pat.replace(f'##{n}',f'(?P<d{n}>.*?)')
    for n in range(num_tokens):
        # might need to change this to not match slashes
        pat = pat.replace(f'#{n}',f'(?P<n{n}>.*)')
    return pat

files = glob(to_glob(normpath(args.p1)),recursive=True)
regex = to_regex(normpath(args.p1))
outs = []
for fn,fil in enumerate(files):
    match = re.match(regex,fil)
    assert match is not None
    match.groupdict()
    out_path = args.p2
    for k,v in match.groupdict().items():
        if k[0] == 'n':
            out_path = out_path.replace(f'#{k[1:]}',v)
        if k[0] == 'd':
            out_path = out_path.replace(f'##{k[1:]}',v)
    if '%' in out_path:
        out_path = out_path % (fn)
    outs.append(out_path)

for fil,out in zip(files,outs):
    print(fil,'->',out)
print("Copy files here? (y/n)")
if input() == 'y':
    for fil,out in zip(files,outs):
        print(fil,'->',out)
        if args.move:
            Path(out).parent.mkdir(parents=True,exist_ok=True)
            Path(fil).rename(out)
        else:
            Path(out).parent.mkdir(parents=True,exist_ok=True)
            shutil.copytree(fil,out)
else:
    print("Aborting")

