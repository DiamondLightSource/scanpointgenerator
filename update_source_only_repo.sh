#! /bin/bash

VER=$(python -c "from scanpointgenerator.version import __version__; print(__version__)")

echo "" &&
echo "Updating daq-eclipse in GDA. Please wait..." &&
echo "" &&

git clone git@github.com:dls-controls/scanpointgenerator.git /tmp/scanpointgenerator &&
git clone git@github.com:DiamondLightSource/daq-eclipse.git /tmp/daq-eclipse &&
cd /tmp/daq-eclipse &&
git checkout -b spg-release-$VER &&
git rm -r org.eclipse.scanning.points/scripts/scanpointgenerator &&
cp -r ../scanpointgenerator/scanpointgenerator/ org.eclipse.scanning.points/scripts/scanpointgenerator &&
git add -A &&
git commit -m "Update scanpointgenerator to version $VER" &&
git push origin spg-release-$VER

echo "" &&
echo "Update successful"

rm -rf /tmp/scanpointgenerator
rm -rf /tmp/daq-eclipse
