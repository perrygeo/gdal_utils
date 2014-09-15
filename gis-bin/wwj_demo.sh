#!/bin/bash
export CLASSPATH=/opt/wwj/worldwind.jar
export LD_LIBRARY_PATH=/opt/wwj:$LD_LIBRARY_PATH
jython wwj_demo.py
