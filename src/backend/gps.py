#!/usr/bin/python3

#------------------------------STANDARD DEPENDENCIES-----------------------------#
from cmath import sqrt
import os
import sys
from typing import Optional, Dict, List
from xmlrpc.client import Boolean
import math

#-----------------------------3RD PARTY DEPENDENCIES-----------------------------#

class GPS():
    def __init__(self) -> None:
        """ Class dedicated to representing GPS coordinates.
        Handles any operations and calcualtions for GPS's
        """
        pass

    @classmethod
    def get_dist_btwn_cords(cls, x1: float, y1: float, x2: float, y2: float) -> float:
        # TODO: get actual calculation method for this
        summation = math.pow((x1-x2), 2) + math.pow((y1-y2), 2)
        res = math.sqrt(summation)
        return res

    @classmethod
    def is_in_range(cls,
                center_x: float,
                center_y: float,
                x2: float,
                y2: float,
                range: float) -> bool:
        """Util Function to check if the distance between 2 coordinates is within an acceptable range"""
        return cls.get_dist_btwn_cords(center_x, center_y, x2, y2) < range
