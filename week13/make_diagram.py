from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
root = Path(__file__).parent
font = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
bold = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
im = Image.new('RGB',(1500,720),'#eef4f8')
d = ImageDraw.Draw(im)
d.text((55,35),'WEEK 13 | Field knowledge pipeline',font=ImageFont.truetype(bold,42),fill='#142c43')
cards=[('01 CAMERA','RGB mean','Nearest-centroid'),('02 COUNTER','Confirm 1 event','LED ON'),('03 RECORD','Microphone','PCM WAV'),('04 STT','Speech to text','Review / correct'),('05 KNOWLEDGE','JSONL + source','Search + speaker')]
for i,(a,b,c) in enumerate(cards):
    x=40+i*295
    d.rounded_rectangle((x,145,x+245,365),radius=20,fill='white',outline='#7899b5',width=3)
    d.text((x+18,169),a,font=ImageFont.truetype(bold,24),fill='#23628b')
    d.text((x+18,231),b,font=ImageFont.truetype(font,22),fill='#142c43')
    d.text((x+18,275),c,font=ImageFont.truetype(font,19),fill='#44637b')
    if i<4:
        d.line((x+250,255,x+286,255),fill='#23628b',width=5);d.polygon([(x+286,255),(x+274,247),(x+274,263)],fill='#23628b')
d.rounded_rectangle((40,410,1460,650),radius=20,fill='#142c43')
d.text((70,435),'Optional physical LED circuit | ESP32 DevKit',font=ImageFont.truetype(bold,30),fill='white')
for x,label in [(120,'GPIO 23'),(470,'220 ohm'),(820,'LED A (+)'),(1200,'GND / K (-)')]:
    d.rounded_rectangle((x-40,520,x+185,595),radius=10,fill='#f5f9fb')
    d.text((x-25,542),label,font=ImageFont.truetype(font,23),fill='#142c43')
for x in [305,655,1005]:d.line((x,557,x+125,557),fill='#4edb9b',width=6)
im.save(root/'pipeline.png')
