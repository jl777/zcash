#!/bin/sh

TMP_DIR=~/tmp/komodo

# make a tmp directory
mkdir -p $TMP_DIR

binaries=("komodo-cli" "komodod")

for binary in "${binaries[@]}";
    do echo $binary;
    echo $binary;
    cp src/$binary $TMP_DIR

    # find the dylibs to copy for komodod
    DYLIBS=`otool -L $TMP_DIR/$binary | grep "/usr/local" | awk -F' ' '{ print $1 }'`
    echo $DYLIBS

    # copy the dylibs to the tmpdir
    for dylib in $DYLIBS; do cp $dylib $TMP_DIR/; done

    # modify komodod to point to dylibs
    for dylib in $DYLIBS; do install_name_tool -change $dylib @executable_path/`basename $dylib` $TMP_DIR/$binary; done;
done








