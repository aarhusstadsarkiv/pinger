#!/bin/bash
nohup pinger </dev/null >/dev/null 2>&1 &
sleep 3 # need to wait for pinger to start
