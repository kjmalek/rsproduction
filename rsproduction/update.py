import csv


def updateMedia(ds_final, scalar_media, media_ex):
    with open(ds_final, 'r', encoding='utf-8') as dscsv, \
         open(scalar_media, 'r', encoding='utf-8') as scalarcsv, \
         open(media_ex, 'w', encoding='utf-8', newline='') as medupcsv:
        dspace = csv.DictReader(dscsv, delimiter=',')
        scalar = csv.DictReader(scalarcsv, delimiter=',')
        if 'art:thumbnail' not in scalar.fieldnames:
            scalar.fieldnames.append('art:thumbnail')
        headers = scalar.fieldnames
        medwriter = csv.DictWriter(medupcsv, fieldnames=headers)
        medwriter.writeheader()
        for row in scalar:
            identifier = row['dcterms:identifier']
            undraft = row['dcterms:title'].split('-draft')[0]
            dscsv.seek(0)
            for drow in dspace:
                if drow['dcterms.identifier'] == identifier:
                    row['dcterms:title'] = undraft
                    row['art:sourceLocation'] = drow['dc.identifier.uri']
                    html = drow['dc.identifier.uri'].replace('handle', 'html')
                    row['art:url'] = f"{html}/{drow['rs.streamFile']}"
                    if 'rs.thumbFile' in dspace.fieldnames:
                        if drow['rs.thumbFile']:
                            row['art:thumbnail'] = f"{html}/{drow['rs.thumbFile']}"
                    row['scalar:slug'] = identifier
                    handle = drow['dc.identifier.uri'].split('handle/')[1]
                    if '.' not in handle:
                        medwriter.writerow(row)


def newMedia(dcsv, scsv):
    with open(dcsv, 'r', encoding='utf-8') as dscsv, \
         open(scsv, 'w', encoding='utf-8', newline='') as scalarcsv:
        dspace = csv.DictReader(dscsv, delimiter=',')
        scalarfields = ['dcterms:title', 'dcterms:description', 'dcterms:source', 'dcterms:identifier', 'scalar:slug',
                      'art:sourceLocation', 'art:url', 'art:thumbnail']
        scalar = csv.DictWriter(scalarcsv, fieldnames=scalarfields, extrasaction='ignore')
        scalar.writeheader()
        for row in dspace:
            row['dcterms:title'] = row['dc.title']
            row['dcterms:description'] = row['dc.description']
            row['dcterms:source'] = row['dcterms.source']
            row['dcterms:identifier'] = row['dcterms.identifier']
            row['scalar:slug'] = f"{row['rs.originalFile'].split('.')[0]}-draft"
            row['art:sourceLocation'] = row['dc.identifier.uri']
            html = row['dc.identifier.uri'].replace('handle', 'html')
            row['art:url'] = f"{html}/{row['rs.streamFile']}"
            if 'rs.thumbFile' in dspace.fieldnames:
                if row['rs.thumbFile']:
                    row['art:thumbnail'] = f"{html}/{row['rs.thumbFile']}"
            scalar.writerow(row)


def inventoryUpdates(scalar_media, media_ex):
    with open(scalar_media, 'r', encoding='utf-8') as oldcsv, \
         open(media_ex, 'r', encoding='utf-8') as newcsv, \
         open('slug-update.csv', 'w', encoding='utf-8', newline='') as slugcsv:
        old = csv.DictReader(oldcsv)
        new = csv.DictReader(newcsv)
        fieldnames = ['id', 'old slug', 'new slug', 'new url']
        writer = csv.DictWriter(slugcsv, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for row in new:
            identifier = row['dcterms:identifier']
            row['id'] = row['dcterms:identifier']
            row['new slug'] = row['scalar:slug']
            row['new url'] = row['art:url']
            oldcsv.seek(0)
            for orow in old:
                if orow['dcterms:identifier'] == identifier:
                    row['old slug'] = orow['scalar:slug']
            if row['new slug'] != row['old slug']:
                writer.writerow(row)


def updatePages(scalar_pages, pages_ex):
    with open(scalar_pages, 'r', encoding='utf-8') as scalarcsv, \
         open('slug-update.csv', 'r', encoding='utf-8') as slugcsv, \
         open(pages_ex, 'w', encoding='utf-8', newline='') as pageupcsv:
        fieldnames = ['dcterms:title', 'sioc:content', 'scalar:slug']
        writer = csv.DictWriter(pageupcsv, fieldnames=fieldnames, extrasaction='ignore')
        scalar = csv.DictReader(scalarcsv, delimiter=',', quotechar='"')
        update = csv.DictReader(slugcsv, delimiter=',', quotechar='"')
        writer.writeheader()
        for row in scalar:
            slugcsv.seek(0)
            for updateRow in update:
                oldSlug = updateRow['old slug']
                newSlug = updateRow['new slug']
                newUrl = updateRow['new url']
                oldA = f'resource="{oldSlug}" href=""'
                newA = f'resource="{newSlug}" href="{newUrl}"'
                row['sioc:content'] = row['sioc:content'].replace(oldA, newA)
                row['sioc:content'] = row['sioc:content'].replace(oldSlug, newSlug)
            writer.writerow(row)


# phase = input("Enter 'add' for new media items or 'update' for existing items: ")

# if phase == "add":
#     DSpaceCSV = input("DSpace Final collection CSV: ")
#     newMedia(DSpaceCSV)
#     print("Done")

# elif phase == "update":
#     DSpaceCSV = input("DSpace Final collection CSV: ")
#     mediaCSV = input("Scalar media CSV: ")
#     pagesCSV = input("Scalar pages CSV: ")
#     updateMedia(DSpaceCSV, mediaCSV)
#     inventoryUpdates(mediaCSV)
#     updatePages(pagesCSV)