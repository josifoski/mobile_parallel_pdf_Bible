#! /usr/bin/env python3.5
# Python program for creating parallel Bible pdf translations with 1, 2 or more translations one verse per page
# By Aleksandar Josifoski https://about.me/josifsk
# 2017 March; April
# Program is dependend on pyfpdf, most easy way to install pyfpdf is pip install -U fpdf
# Licence free GPL

# You can see correct format for Bible texts as input in /Bibles directory

from fpdf import FPDF
import codecs
import sys
import time
from mppb_imports import Bibliaa, allbooks, bookschapters, book_pos_ends

num_of_translations = 2
dir_in = '/data/git/mobile_parallel_pdf_Bible/'
bibles_dirs_in = [dir_in + '/Bibles/ENG/ENG_WEB/', dir_in + '/Bibles/MKD/MKD_konstantinov/']
translations_titles = ['English World English Bible', 'Macedonian Konstantinov']
# You can change in next line name for generated pdf
output_name = dir_in + 'output.pdf'
# After creating pdf, you can optionally use automatically crop pages option in your pdf viewer
# afaik xodo is best pdf program for reading (+editing didn't tested it much) for mobile devices

# btest is for only generating output for Genesis and Esther, since creating pdf for all books will
# take some time from ~1/2 hour .. more hours depending on num_of_translations and processor speed.
btest = False           # set to False to generate expected goal, with True only for scope of books few lines bellow
create_TOC_only = True  # First, you will need to start program with True for create_TOC_only, and False for btest
                        # and in next line tocpages =  to put number of table of contents pages
tocpages = 8

if btest:
    books = ['Genesis', 'Esther']
else:
    books = allbooks

# Since Esther 8:9 is significant verse as largest while defining all related values, you should
# set values compatible for that verse to fit in one page
# You can experiment with bellow values for font sizes, width and height depending is target for smartphone or tablet
font_name = 'DejaVuSans'
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf' # for using on windows directory separator is \\
font_title_size = 11
font_translations_size = 9
font_booksconn_size = 9
font_chapterconn_size = 8
font_text_size = 9
font_reff_size = 6
width_mm = 55
height_mm_per_translation = 80

# starting from here bellow you don't have to touch anything, but if you touch is fine
sumbookchapter = 0
def calculate_next_bookchapter_page(book, chapter):
    global sumbookchapter
    if btest:
        if chapter == 1:
            sumbookchapter += int(Bibliaa[books[bi - 1]][-1].split(':')[1])
        else:
            sumbookchapter += int(Bibliaa[book][chapter - 2].split(':')[1])
    else:
        if chapter == 1:
            sumbookchapter = book_pos_ends[allbooks[bi - 1]]
        else:
            sumbookchapter += int(Bibliaa[book][chapter - 2].split(':')[1])
    return sumbookchapter

time1 = time.time()
def calculate_time():
    '''function to calculate elapsed time'''
    time2 = time.time()
    hours = int((time2-time1)/3600)
    minutes = int((time2-time1 - hours * 3600)/60)
    sec = time2 - time1 - hours * 3600 - minutes * 60
    print("processed in %dh:%dm:%ds" % (hours, minutes, sec))

# Define default starting pdf values
pdf = FPDF(orientation = 'P', unit = 'mm', format = (width_mm, num_of_translations * height_mm_per_translation))
pdf.set_auto_page_break(auto = True, margin = 0.3)
pdf.set_compression(compress = False)
pdf.set_margins(left = 0.1, top = 0.1, right = 0.1)
pdf.add_page()

# Generate TOC
pdf.add_font(font_name, '', font_path, uni = True)
pdf.set_font(family = font_name, style = '', size = font_title_size)
pdf.set_text_color(r = 255, g = 0, b = 0)
text = 'Parallel Bible Translations'
pdf.cell(w=0, h=9, txt=text, border=0, ln=1, align='L', fill=0)
pdf.set_font(family = font_name, style = '', size = font_translations_size)
pdf.set_text_color(r = 0, g = 0, b = 0)
for text in translations_titles:
    pdf.cell(w=0, h=4, txt=text, border=0, ln=1, align='L', fill=0)
pdf.ln()
pdf.ln()

# pdf.add_page()
for book in books:
    print('TOC for ' + book)
    bi = books.index(book)
    text = book
    pdf.set_font(family = font_name, style = '', size = font_booksconn_size)
    pdf.set_text_color(r = 0, g = 0, b = 0)
    pdf.cell(w=0, h=4, txt=text, border=0, ln=1, align='L', fill=0)
    pdf.set_font(family = font_name, style = '', size = font_chapterconn_size)
    num2ln = 11
    ipos = 0
    pdf.set_text_color(r = 0, g = 0, b = 255)
    for i in range(1, bookschapters[book] + 1):
        ipos += 1
        if i < 10:
            text = '   ' + str(i)
        else:
            text = ' ' + str(i)
        if i > 99:
            num2ln = 8
        else:
            num2ln = 11
        # connect with page
        if book == books[0] and i == 1:
            pageconnect = tocpages + 1
        else:
            pageconnect = tocpages + 1 + calculate_next_bookchapter_page(book, i)
        
        mylink = pdf.add_link()
        pdf.set_link(mylink, y = 0.0, page = pageconnect)
        pdf.write(h=4, txt=text, link = mylink)
        if ipos % num2ln == 0:
            pdf.ln()
            ipos = 0
    pdf.ln()
    pdf.ln()

if create_TOC_only:
    for i in range(2000):
        pdf.add_page()
    print('Generating ' + output_name)
    pdf.output(name = output_name, dest = 'F')
    sys.exit()

# Fill parallel texts
if not create_TOC_only:
    for book in books:
        bi = allbooks.index(book) + 1
        l = []
        print('processing ' + book)
        for translation_dir in bibles_dirs_in:
            prepare_filename = translation_dir + '%02d' % bi + '-' + book + '.' + translation_dir.split('/')[-2] + '.txt'
            with codecs.open(prepare_filename, 'r', 'utf-8') as fi:
                ll = []
                for line in fi:
                    line = line.strip()
                    if line.startswith('{i'):
                        continue
                    else:
                        ll.append(line)
            l.append(ll)
                
        # write book in pdf
        pdf.set_text_color(r = 0, g = 0, b = 0)
        verses_len = len(l[0])
        for verse_index in range(verses_len):
            pdf.add_page()
            bpass = True
            for translation_index in range(num_of_translations):
                rawline = l[translation_index][verse_index]
                verse_reff = rawline.split()[0].strip('{}')
                verse_chapter_int = int(verse_reff.split(':')[0].strip())
                verse_num = verse_reff.split(':')[1].strip()
                verse_text = ' '.join(rawline.split()[1:])
                if bpass:
                    pdf.set_font(family = font_name, style = '', size = font_reff_size)
                    if verse_num == '1':
                        text = book + ' ' + verse_reff + ' (' + Bibliaa[book][verse_chapter_int - 1].split(':')[1] + ')'
                        pdf.set_text_color(r = 0, g = 0, b = 255)
                    else:
                        text = book + ' ' + verse_reff
                    pdf.cell(w=0, h=4, txt=text, border=0, ln=1, align='R', fill=0)
                    pdf.ln()
                    text = verse_text
                    pdf.set_font(family = font_name, style = '', size = font_text_size)
                    pdf.set_text_color(r = 0, g = 0, b = 0)
                    pdf.write(h=4, txt=text)
                    pdf.ln()
                    pdf.ln()
                    bpass = False
                else:
                    text = verse_text
                    pdf.write(h=4, txt=text)
                    # next part is for using more then 2 translations
                    if translation_index < num_of_translations - 1:
                        pdf.ln()
                        pdf.ln()

# Finally generate pdf
print()
print('Generating ' + output_name + '. This will take some time..')
pdf.output(name = output_name, dest = 'F')
calculate_time()
print('Done.')
