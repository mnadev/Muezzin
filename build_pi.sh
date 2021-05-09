#!/usr/bin/env bash
echo "Building App"
pyinstaller -y --clean --windowed muezzin.spec > /dev/null
echo "Packaging"
pushd dist > /dev/null
tar czf ../../muezzin.tar muezzin/ > /dev/null
popd > /dev/null
cd ..
echo "Extracting"
mkdir muezzin_app
mv muezzin.tar muezzin_app
cd muezzin_app
tar -xvf muezzin.tar > /dev/null
echo "Package succesfully built"


