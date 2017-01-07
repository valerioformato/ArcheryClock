import os
import sys

sys.path.insert(0, os.path.abspath('clock'))
from clock_class import ClockDisplay

def main():
    window = ClockDisplay()
    window.StartApp()

if __name__ == '__main__' : main()
