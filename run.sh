#!/bin/bash
setsid nohup pinger &> /dev/null &
sleep 3 # need to wait for pinger to start
