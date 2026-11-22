import os
import time
import threading
import requests
import math
import operator as op
from flask import Flask
import telebot
def W(*n):
    return chr(0)[:0].join(map(chr, n))
TOKEN = os.environ.get(W(84,79,75,69,78))
bot = telebot.TeleBot(TOKEN)
app = Flask(W(109,97,115,104,105,110,107,97))
CHAT_ID = None
S1 = W(66,84,67)
S1 += W(85,83,68,84)
S2 = W(69,84,72)
S2 += W(85,83,68,84)
S3 = W(83,79,76)
S3 += W(85,83,68,84)
S4 = W(66,78,66)
S4 += W(85,83,68,84)
S5 = W(88,82,80)
S5 += W(85,83,68,84)
S6 = W(68,79,71,69)
S6 += W(85,83,68,84)
SYMBOLS = [S1]
SYMBOLS += [S2]
SYMBOLS += [S3]
SYMBOLS += [S4]
SYMBOLS += [S5]
SYMBOLS += [S6]
positions = {}
balance = 500.0
H = W(104,116,116,112,115)
H += W(58,47,47)
T1 = W(116,101,115,116,110,101,116)
T1 += W(46,98,105,110,97,110,99,101)
T2 = W(46,118,105,115,105,111,110)
B1X = W(97,112,105,46,98,105,110,97,110,99,101)
B2X = W(46,99,111,109)
BASE1 = H + T1 + T2
BASE2 = H + B1X + B2X
K1 = W(47,97,112,105,47,118,51)
K2 = W(47,107,108,105,110,101,115)
KLINE = K1 + K2
P1 = W(47,97,112,105,47,118,51)
P2 = W(47,116,105,99,107,101,114)
P3 = W(47,112,114,105,99,101)
PRICE = P1 + P2 + P3
SP = chr(32)
NL = chr(10)
A1 = W(82,83,73)
A1 += W(95,79,75)
A2 = W(82,83,73)
A2 += W(95,78,79)
B1 = W(69,77,65)
B1 += W(95,79,75)
B2 = W(69,77,65)
B2 += W(95,78,79)
C1 = W(84,114,101,110,100)
C1 += W(95,79,75)
C2 = W(84,114,101,110,100)
C2 += W(95,78,79)
D1 = W(83,116,111,99,104)
D1 += W(95,79,75)
D2 = W(83,116,111
