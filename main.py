import os
import sys

sys.path.insert(0, os.path.abspath('src'))
from clock_display_osx import ClockDisplay

def main():
    myclock = ClockDisplay()
    myclock.StartApp()

if __name__ == '__main__' : main()
