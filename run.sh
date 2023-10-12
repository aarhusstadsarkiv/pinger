#!/bin/bash
setsid nohup pinger > /dev/null 2> ./nohup.err < /dev/null &
sleep 5 # need to wait for pinger to start
