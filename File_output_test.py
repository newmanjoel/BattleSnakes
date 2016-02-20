# -*- coding: utf-8 -*-
"""
Created on Fri Feb 19 19:26:25 2016

@author: joelnewman
""" 


with open("output.txt",'w') as fp:
    for x in range(90):
        fp.write(repr(x)+"\n")

print "all done"
    