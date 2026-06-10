#!/bin/bash
ansible-galaxy collection build --force && ansible-galaxy collection install mrchainman-custom-1.0.0.tar.gz --force
