#/usr/env/bin/python
# -*- coding: utf-8 -*-

import morpha_fi

def main():
    pass

def pos_tag(text):
    analysis = morpha_fi.analyse_morphologically(text)
    result = morpha_fi.pos_tag(analysis)
    return result

def quick_pos_tag(text):
    result = pos_tag(text)
    return result

if __name__ == '__main__':
    main()
