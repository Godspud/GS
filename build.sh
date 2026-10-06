#!/usr/bin/env bash

rm -rf out.txt

get_entries() {
    echo $(ls example)
}
entries="$(get_entries '.')"
echo "$entries"
for dir in $entries; do
    echo "$dir"
    python3 main.py "example/${dir}" >> "out.txt"
done

#chapter_dirs="$(get_entries '.')"
#for dir in $chapter_dirs; do
#    if [ -f ".pandoc/decorators/${dir:2}.tex" ]; then
#        cmd_body+=".pandoc/decorators/${dir:2}.tex "
#        echo "|---- ${dir:2} (with decorator)"
#    else
#        echo "|---- ${dir:2} (no decorator file)"
#    fi
#
#    chapter_entries="$(get_entries $dir)"
#    for entry in $chapter_entries; do
#        if [[ $entry != *".md" ]]; then
#            continue;
#        fi
#        echo "|  |- ${entry:2}"
#        cmd_body+="$entry "
#    done
#    unset chapter_entries
#    echo "|"
#done
#
#cmd_body+="LICENSE.md"
#if [ -v ADD_COMMIT ]; then
#    awk -v HASH=`git rev-parse HEAD`  '!found && /header-includes/ { print "   |\n   | based on commit: " HASH ; found=1 } 1' .pandoc/pandoc.yaml | tee .pandoc/pandoc_1.yaml
#    mv .pandoc/pandoc_1.yaml .pandoc/pandoc.yaml
#fi
#
#if [ -v ON_CODEBERG ]; then
#    echo "CODEBERG env identified, creating output directory"
#    mkdir output
#    OUTPUT_FOLDER="output/" 
#    echo $OUTPUT_FOLDER
#fi
#
#$(pandoc $pandoc_flags $cmd_body .pandoc/pandoc.yaml -o $OUTPUT_FOLDER$pandoc_filename)
#