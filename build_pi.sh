#!/usr/bin/env bash
echo "Building App";
pyinstaller -y --clean --windowed muezzin.spec > /dev/null;
echo "Packaging";
cd dist > /dev/null;
touch ../../muezzin.tar;
chmod 644 ../../muezzin.tar;
tar czf ../../muezzin.tar muezzin/ > /dev/null;
cd .. > /dev/null;
cd ..;
echo "Extracting";
mkdir muezzin_app;
mv muezzin.tar muezzin_app;
cd muezzin_app;
tar -xvf muezzin.tar > /dev/null;
echo "Package succesfully built";


