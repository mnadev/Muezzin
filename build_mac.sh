#!/usr/bin/env bash
pyinstaller -y --clean --windowed muezzin.spec
pushd dist
hdiutil create ./muezzin.dmg -srcfolder muezzin.app -ov
popd
