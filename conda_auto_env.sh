#!/bin/bash

# conda-auto-env automatically activates a conda environment when
# entering a folder with an environment.yml file.
#
# If the environment doesn't exist, conda-auto-env creates it and
# activates it for you.
#
# To install add this line to your .bashrc or .bash-profile:
#
#       source /path/to/conda_auto_env.sh
#

function conda_auto_env() {
  conda_auto_env_path=".conda.yml"
  #count folder depth by counting slashes in path
  depth=`pwd | grep -o / | wc -l`
  count=0
  while [ $count -le $depth ]
  do
    #echo "looking for $conda_auto_env_path"
    if [ -e $conda_auto_env_path ]; then
      #echo "$conda_auto_env_path file found"
      ENV=$(head -n 1 $conda_auto_env_path | cut -f2 -d ' ')
      # Check if you are already in the environment
      if [[ $PATH != *$ENV* ]]; then
        # Check if the environment exists
        conda activate $ENV
        if [ $? -eq 0 ]; then
          :
        else
          echo "Conda env '$ENV' doesn't exist."
          #conda env create -q
          #source activate $ENV
        fi
      fi
      return 0
    fi
    conda_auto_env_path="../$conda_auto_env_path"
    count=$(($count + 1))
  done
  #echo "No conda env specified"
}
#conda_auto_env
#export PROMPT_COMMAND=conda_auto_env

