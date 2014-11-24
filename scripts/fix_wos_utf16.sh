#!/bin/bash

inputdir=$1

ls "$inputdir" | while read di; do
  ls "$inputdir/$di/"*.txt | while read f; do
    if file "$f" | grep -i "little-endian utf-16" > /dev/null; then
      mv "$f" "$f.utf16"
      echo "converting $f.utf16 into $f"
      if ! iconv -f "UTF-16LE" -t "UTF-8" "$f.utf16" > "$f"; then
        echo "!! WARNING !! Could not fix file $f"
        mv "$f.utf16" "$f"
      fi
    fi
  done
done

