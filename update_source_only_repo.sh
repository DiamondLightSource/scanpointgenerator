#! /bin/bash

if [ -z "$1" ]
  then
    echo "Must provide a release version"
    exit 1
else
    VER="$1"
fi

git clone git@github.com:dls-controls/scanpointgenerator.git /tmp/scanpointgenerator &&
git clone git@github.com:DiamondLightSource/daq-eclipse.git /tmp/daq-eclipse &&
cd /tmp/daq-eclipse &&
git checkout -b spg-release-$(VER) &&
cp -r ../scanpointgenerator/scanpointgenerator/ org.eclipse.scanning.points/scripts/scanpointgenerator &&
git add -A &&
git commit -m "Update scanpointgenerator to version $(VER)"
git push origin release-$(VER)

rm -rf /tmp/scanpointgenerator
rm -rf /tmp/daq-eclipse
