#!/bin/bash

# Fix the apt sources.list for legacy Ubuntu release
sudo sed -i 's|http://\(.*\.\)\?archive.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g; s|http://security.ubuntu.com/ubuntu|http://old-releases.ubuntu.com/ubuntu|g' /etc/apt/sources.list

# Update `apt` package index.
sudo apt-get update
