#!/usr/bin/env python
# Based on msgfmt.py from Python generic tools

import os
import sys
import struct
import array
from pathlib import Path
import re

def generate():
    """
    Generate binary .mo files for all .po files in the locale directory.
    """
    base_dir = Path('.')
    locale_dir = base_dir / 'locale'
    
    version = 0
    
    for polang_dir in locale_dir.iterdir():
        if not polang_dir.is_dir():
            continue
            
        lc_messages = polang_dir / 'LC_MESSAGES'
        if not lc_messages.is_dir():
            continue
            
        for po_file in lc_messages.glob('*.po'):
            mo_file = po_file.with_suffix('.mo')
            print(f"Compiling {po_file} -> {mo_file}")
            make(po_file, mo_file)

def make(filename, outfile):
    ID = 1
    STR = 2

    messages = {}
    
    # Simple PO parser
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    section = None
    msgid = b''
    msgstr = b''


    def unescape(s):
        return s.replace(r'\"', '"').replace(r'\n', '\n').replace(r'\\', '\\')

    for l in lines:
        l = l.strip()
        if not l:
            continue
        if l.startswith('#'):
            continue
            
        # Handle quoted strings
        match = re.search(r'^msgid\s+"(.*)"$', l)
        if match:
            if section == STR:
                messages[msgid] = msgstr
            section = ID
            msgid = unescape(match.group(1)).encode('utf-8')
            msgstr = b''
            continue

        match = re.search(r'^msgstr\s+"(.*)"$', l)
        if match:
            section = STR
            msgstr = unescape(match.group(1)).encode('utf-8')
            continue
            
        # Continue strings (multiline)
        match = re.search(r'^"(.*)"$', l)
        if match:
            if section == ID:
                msgid += unescape(match.group(1)).encode('utf-8')
            elif section == STR:
                msgstr += unescape(match.group(1)).encode('utf-8')

    if section == STR:
        messages[msgid] = msgstr

    # Filter out empty translations (except the header which has empty msgid)
    # If msgstr is empty and msgid is NOT empty, it means untranslated.
    # We should exclude it so gettext falls back to msgid.
    final_messages = {}
    for mid, mstr in messages.items():
        if mid == b'' or mstr != b'':
            final_messages[mid] = mstr
            
    messages = final_messages

    # Compute binary data
    keys = sorted(messages.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for id in keys:
        # For each string, we need offset and length
        # IDs
        offsets.append((len(ids), len(id), len(strs), len(messages[id])))
        ids += id + b'\0'
        strs += messages[id] + b'\0'
        
    output_count = len(keys)
    
    # Header: magic, version, count, start_of_msgidx, start_of_msgstr, 0, 0
    keystart = 7 * 4 + 16 * output_count # Header depends on count? No.
    # Header is 28 bytes usually (7 integers) if I recall?
    # Python struct: I I I I I I I
    
    # magic = 0x950412de
    # version = 0
    # number of strings
    # offset of table with original strings
    # offset of table with translation strings
    # size of hashing table
    # offset of hashing table
    
    magic = 0x950412de
    version = 0
    
    # 7 * 4 bytes for header
    # 2 * 4 bytes * count for offsets
    
    header_size = 28
    
    start_of_msgidx = header_size
    start_of_msgstr = start_of_msgidx + (8 * output_count)
    
    # The actual strings start after the tables
    start_of_data = start_of_msgstr + (8 * output_count)
    
    # Pack header
    # magic, version, count, msgidx_off, msgstr_off, hash_size, hash_off
    header = struct.pack('Iiiiiii', 
                         magic, 
                         version, 
                         output_count, 
                         start_of_msgidx, 
                         start_of_msgstr, 
                         0, 0)
                         
    # Pack tables
    # O1, L1, O2, L2 ...
    # Offsets in table are OFFSETS FROM START OF FILE found in ids/strs blob
    # ids blob starts at start_of_data
    # strs blob starts at start_of_data + len(ids)
    
    idx_content = b''
    str_content = b''
    
    current_ids_addr = start_of_data
    current_strs_addr = start_of_data + len(ids)
    
    for (id_off, id_len, str_off, str_len) in offsets:
        idx_content += struct.pack('ii', id_len, current_ids_addr + id_off)
        str_content += struct.pack('ii', str_len, current_strs_addr + str_off)
    
    with open(outfile, 'wb') as f:
        f.write(header)
        f.write(idx_content)
        f.write(str_content)
        f.write(ids)
        f.write(strs)
        
if __name__ == "__main__":
    generate()
