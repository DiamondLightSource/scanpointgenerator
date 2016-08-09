#! /bin/bash

git clone git@github.com:dls-controls/scanpointgenerator.git /tmp/scanpointgenerator && 
cd /tmp/scanpointgenerator && 
git checkout -b source-only &&
git pull origin master &&
git filter-branch -f --subdirectory-filter scanpointgenerator/ --prune-empty --tag-name-filter cat -- --all &&
git remote add upstream git@github.com:dls-controls/scanpointgenerator.git &&
echo "sudo: false
language: python
install: cd .. && python -c 'import scanpointgenerator'
script: nosetests" > /tmp/scanpointgenerator/.travis.yml &&
git add .travis.yml &&
git commit -m "Add .travis.yml file" &&
git push --force upstream source-only &&
cd .. &&
rm -rf scanpointgenerator
