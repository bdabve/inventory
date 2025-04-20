#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Functions to work with for all project

from datetime import date
from ummalqura.hijri_date import HijriDate
import openpyxl
from openpyxl.utils import get_column_letter
from django.utils.timezone import is_aware
from datetime import datetime
import os


def write_to_excel_g(fields, queryset, filename_prefix):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Mouvements"

    # Write header
    for col_num, field in enumerate(fields, 1):
        col_letter = get_column_letter(col_num)
        ws[f'{col_letter}1'] = field.replace('_', ' ').capitalize()

    # Write data
    for row_num, row in enumerate(queryset.values_list(*fields), 2):
        for col_num, value in enumerate(row, 1):
            # Handle timezone-aware datetime objects
            if isinstance(value, datetime) and is_aware(value):
                value = value.replace(tzinfo=None)
                value = value.strftime('%d-%m-%Y')
            ws.cell(row=row_num, column=col_num, value=value)

    # Save with a timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{filename_prefix}_{timestamp}.xlsx"
    filepath = os.path.join('media', 'exports', filename)

    # Ensure directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    wb.save(filepath)


def hijri_():
    """This functions returns a hijri date"""
    tday = date.today()
    hijri = HijriDate(tday.year, tday.month, tday.day, gr=True)
    return hijri
