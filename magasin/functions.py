#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Functions to work with for all project

import xlsxwriter
import os
from datetime import date
from ummalqura.hijri_date import HijriDate


def write_to_excel(desc, rows, date_):
    '''
    Write SQL Query to xlsx file
    desc : colnames
    rows : data
    date_ : to name the file.
    '''
    if os.path.exists('Etats'):
        print('exist')
    else:
        os.mkdir('Etats')

    fname = './Etats/etat_' + date_ + '.xlsx'
    if os.path.exists(fname):
        # remove old file with the same name
        os.remove(fname)

    # formate rows and description and headers
    wbook = xlsxwriter.Workbook(fname, {'remove_timezone': True})
    desc_format = wbook.add_format({'font_name': 'Times New Roman',
                                    'bold': True,
                                    'font_size': 16,
                                    'border': 1,
                                    'align': 'center',
                                    'valign': 'center'})

    rows_format = wbook.add_format({'font_name': 'Times New Roman', 'font_size': 14, 'border': 1})
    date_format = wbook.add_format({'font_name': 'Times New Roman', 'font_size': 14, 'border': 1, 'num_format': 'dd mmmm yyyy'})
    money_format = wbook.add_format({'font_name': 'Times New Roman', 'font_size': 14, 'border': 1, 'num_format': '# ##0,00 €'})

    wsheet = wbook.add_worksheet(date_)
    wsheet.set_row(3, 25)               # set the height for row 0
    wsheet.set_column('A:A', 25)        # set the length for column A:A (movement_date)
    wsheet.set_column('B:B', 18)        # set the length for column B:B (code)
    wsheet.set_column('C:C', 32)        # set the length for column C:C (designation)
    wsheet.set_column('D:D', 18)        # set the length for column D:D (movement)
    wsheet.set_column('E:E', 12)        # set the length for column E:E (qte)
    wsheet.set_column('F:F', 18)        # set the length for column F:F (prix)
    wsheet.set_column('G:G', 18)        # set the length for column G:G (valeur)

    # write title and date
    title_format = wbook.add_format({'font_name': 'Times New Roman',
                                     'font_size': 20,
                                     'bold': True,
                                     'italic': True,
                                     'valign': 'center'})
    wsheet.merge_range('A1:C1', 'Etats Du ' + date_, title_format)
    # date
    tday = date.today().strftime('%d/%m/%Y')
    tday_format = wbook.add_format({'font_name': 'Times New Roman', 'font_size': 14, 'valign': 'right'})
    wsheet.merge_range('F1:G1', 'Bou Ismail Le: ' + tday, tday_format)

    # write description
    excel_row = 3
    excel_col = 0
    for des in desc:
        wsheet.write(excel_row, excel_col, des.title(), desc_format)
        excel_col += 1

    # write rows
    excel_row = 4
    for row in rows:
        excel_col = 0
        for i, r in enumerate(row):
            if i == 0:
                wsheet.write(excel_row, excel_col, r, date_format)
            elif i == 5 or i == 6:        # prix, valeur index
                wsheet.write(excel_row, excel_col, r, money_format)
            else:
                rows_format.set_num_format('0')
                wsheet.write(excel_row, excel_col, r, rows_format)
            excel_col += 1
        excel_row += 1

    wbook.close()


def hijri_():
    """This functions returns a hijri date"""
    tday = date.today()
    hijri = HijriDate(tday.year, tday.month, tday.day, gr=True)
    return hijri
