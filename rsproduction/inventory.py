import os
import shutil
import csv
import platform

from . import processing


def submitInventory(project_id, series_num, sub_dir, out_dir, process_opt):
    sourceFolders = []
    files = []
    filename = f'{out_dir}/temp/SAFinventory.csv'

    # isbn = input("Enter the project's ISBN: ")
    # seriesNum = input("Enter the next available series number: ")
    isbn = int(project_id)
    seriesNum = int(series_num)

    # Scan the directory for "Source" directories
    with os.scandir(sub_dir) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                os.renames(f'{sub_dir}/{entry.name}', f'{sub_dir}/unknown/{entry.name}')
            elif not entry.name.startswith('.') and entry.is_dir():
                sourceFolders.append(entry.name)

    # Scan the "Source" directories and store the name of the source directory and the filename in
    # an array of dictionaries
    for folder in sourceFolders:
        path = f"{sub_dir}/{folder}"
        with os.scandir(path) as it:
            for entry in it:
                if not entry.name.startswith('.') and entry.is_file():
                    files.append({'dcterms.source': folder, 'rs.originalFile': entry.name})
                
    # Add identifiers in the dcterms.identifier field of each dictionary
    for file in files:
        file['dcterms.identifier'] = f"{isbn}_{seriesNum:03}"
        file['dc.title'] = f"{file['dcterms.identifier']}-draft"
        description, ext = os.path.splitext(file['rs.originalFile'])
        file['dc.description'] = description
        seriesNum += 1

    # Move files to directory "archive" and rename using the new identifiers
    for file in files:
        old = f"{sub_dir}/{file['dcterms.source']}/{file['rs.originalFile']}"
        oldfilename, ext = os.path.splitext(old)
        new = f"{sub_dir}/{file['dcterms.identifier']}{ext}"
        os.renames(old, new)
        
    # Run file conversions
    if process_opt == 1:
        pass
    elif process_opt == 2:
        fileProcessing.fileConversions(sub_dir)
    elif process_opt == 3:
        fileProcessing.fileOptimizations(sub_dir)
    
    for file in files:
        identifier = file['dcterms.identifier']
        optfiles = []
        with os.scandir(f'{sub_dir}/') as it:
            for entry in it:
                if entry.name.startswith(identifier):
                    optfiles.append(entry.name)
        filenames = "|".join(optfiles)
        file['file'] = filenames
        for optfile in optfiles:
            filen = os.path.splitext(optfile)[0]
            if filen.endswith('_M'):
                pass
            elif filen.endswith('_TH'):
                file['rs.thumbFile'] = optfile
            else:
                file['rs.streamFile'] = optfile
    # Output the dictionaries as rows in a CSV
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['dc.title', 'dc.description', 'rs.originalFile', 'dcterms.source', 'dcterms.identifier',
                      'dcterms.abstract', 'rs.thumbFile', 'rs.streamFile', 'file']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
        writer.writeheader()

        for file in files:
            writer.writerow(file)

    print(f"The files have been inventoried in {filename}, renamed, converted (if needed), "
          f"and moved to their parent directory.")
    return filename


def updateInventory(csvIn, sub_dir, out_dir, process_opt):
    DSdraft = csvIn
    SAFout = f'{out_dir}/SAFinventory.csv'
    
    with open(DSdraft, 'r') as readcsv, \
         open(SAFout, 'w') as writecsv:
        fieldnames = ['dc.title', 'dc.description', 'rs.originalFile', 'dcterms.source', 'dcterms.identifier',
                      'rs.streamFile', 'rs.thumbFile', 'file']
        writer = csv.DictWriter(writecsv, fieldnames=fieldnames, extrasaction='ignore')
        reader = csv.DictReader(readcsv)
        writer.writeheader()

        if process_opt == 1:
            pass
        elif process_opt == 2:
            fileProcessing.fileConversions(sub_dir)
        elif process_opt == 3:
            fileProcessing.fileOptimizations(sub_dir)
        
        for row in reader:
            identifier = row['dcterms.identifier']
            optfiles = []
            # Remove "-draft" from the title
            row['dc.title'] = row['dc.title'].split("-draft")[0]
            with os.scandir(sub_dir) as it:
                for entry in it:
                    if entry.name.startswith(identifier):
                        optfiles.append(entry.name)
            filenames = "|".join(optfiles)
            row['file'] = filenames
            for optfile in optfiles:
                filen = optfile.split('.')[0]
                if filen.endswith('_M'):
                    pass
                elif filen.endswith('_TH'):
                    row['rs.thumbFile'] = optfile
                else:
                    row['rs.streamFile'] = optfile
            if not optfiles:
                pass
            else:
                writer.writerow(row)
    
    print(f"The new files have been inventoried in {SAFout}.")
    arc_dir = f'{out_dir}/archives'
    inventory = SAFout
    SimpleArchiveBuilder.run(out_dir, sub_dir, arc_dir, inventory)
