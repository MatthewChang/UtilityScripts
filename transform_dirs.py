from glob import glob
import shutil
from pathlib import Path
import re
from posixpath import normpath
import re
import argparse
parser = argparse.ArgumentParser(description='')
parser.add_argument('p1')
parser.add_argument('p2')
parser.add_argument('--move',action='store_true')
args = parser.parse_args()
num_tokens = 5
'''
python ~/UtilityScripts/transform_dirs.py  "20bn-something-something-v2-#1.zip" "something/20bn-something-something-v2-#1.zip"
python ~/UtilityScripts/transform_dirs.py  "fil#1.txt" 'nested#1/fil.txt'
python ~/UtilityScripts/transform_dirs.py  "##1/fil.txt" 'out/fil.txt'
python ~/UtilityScripts/transform_dirs.py  "##1/nested#1/fil.txt" 'out/fil#1.txt'
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
for fil in files:
    match = re.match(regex,fil)
    assert match is not None
    match.groupdict()
    out_path = args.p2
    for k,v in match.groupdict().items():
        print(k,v)
        if k[0] == 'n':
            out_path = out_path.replace(f'#{k[1:]}',v)
        if k[0] == 'd':
            out_path = out_path.replace(f'##{k[1:]}',v)
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
            shutil.copy(fil,out)
else:
    print("Aborting")

