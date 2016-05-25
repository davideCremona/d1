#!/bin/bash
source d1.cfg
if [ -z "$2" ] && [ "$1" = "help" ]
  then
    echo "to change configurations, edit the d1.cfg file"
    echo "you can change:"
    echo "- iNARK directory: relative path to the directory where the iNARK executable is placed"
    echo "- type: type of search performed by iNARK"
    echo "- depth: depth of the search performed by iNARK"
    echo "- high priority tasks list"
    echo "- low priority tasks list"
    echo "d1 usage: "
    echo "./d1 [input xml file path] [output directory path]"
    echo "[input xml file path] is the path to the xml that describes the layered architecture"
    echo "[output directory path] is the path to the output directory where to store the xml files that does not contains paths from source tasks to target tasks"
    exit
fi
if [ -z "$1" ] && [ -z "$2"]
    then
        echo "usage: "
        echo "./d1 [input xml file path] [output directory path]"
    else
        xmlFile=$1
        dirname=$2

        mkdir -p $dirname/accepted
        mkdir -p $dirname/rejected

        echo "	If $dirname is already used, files will be overwritten"
        echo "	Generating configurations from $xmlFile... (will be available in $dirname)"
        python fileGenerator.py $xmlFile 2 $dirname

        #check all the combinations of source tasks and target tasks
        #for each filename
        for filename in $dirname/*.xml; do
          echo "  checking $filename with settings: type:$iNARK_type - depth=$iNARK_depth..."
          allok=1
          #check all the combinations
          for low in ${low_priority_tasks[*]}; do

            #reset flag for the hp task
            
            for high in ${high_priority_tasks[*]}; do
              echo "iNARK --input $filename --source $low --target $high --type $iNARK_type --depth $iNARK_depth"
              #call iNARK for this combination
              ./$iNARK_directory/iNARK --input $filename --source $low --target $high --type $iNARK_type --depth $iNARK_depth
              if [ "$?" -ne "0" ]
                then
                  allok=0
              fi
            echo "first loop ward"
            done
            echo "first loop end, second loop ward"
          done
          echo "second loop end, moving file"
          #all configurations checked, move to rejected if allok=0
          if [ "$allok" -eq "0" ]
            then
              mv $filename $dirname/rejected
            else
              mv $filename $dirname/accepted
          fi

        echo "third loop ward"
        done
        echo "  d1 finished. "
        echo "  Configurations files that are ok are available in $dirname/accepted"
        echo "  COnfigurations files that are not ok are available in $dirname/rejected"
fi
