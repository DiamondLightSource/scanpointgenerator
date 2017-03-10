#! /bin/bash

VER=$(python -c "from scanpointgenerator.version import __version__; print(__version__)")

echo "" &&
echo "Updating SPG in eclipse/scanning. Please wait..." &&
echo "" &&

git clone git@github.com:dls-controls/scanpointgenerator.git /tmp/scanpointgenerator &&
git clone git@github.com:eclipse/scanning.git /tmp/scanning &&
cd /tmp/scanning &&
git checkout -b spg-release-$VER &&
git rm -r org.eclipse.scanning.points/scripts/scanpointgenerator &&
cp -r ../scanpointgenerator/scanpointgenerator/ org.eclipse.scanning.points/scripts/scanpointgenerator &&
git add -A &&
git commit -m "Update scanpointgenerator to version $VER" &&
git push origin spg-release-$VER &&

echo "" &&
echo "Update successful"

rm -rf /tmp/scanpointgenerator
rm -rf /tmp/scanning
