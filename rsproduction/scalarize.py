import csv
import os
import shutil
import collections
import json

from bs4 import BeautifulSoup
import pypandoc
import requests

from . import saf_builder
from . import csv2metadata
from . import processing


def no_media(man_file, out_dir):
    """Convert docx file to Scalar formatted CSV without media"""
    out_temp = f'./{out_dir}/temp'
    os.makedirs(out_temp)
    html_man = f"{out_temp}/manuscript.html"
    pypandoc.convert_file(man_file, 'html', format='docx', outputfile=html_man)
    with open(html_man, encoding='utf-8') as man:
        soup = BeautifulSoup(man, 'html.parser')
    for tag in soup.find_all('h6'):
        filename = tag.contents[0].split(' | ')[0]
        slug = f"{filename.split('.')[0]}-draft"
        previous = tag.find_previous("p")
        if previous.contents[0].name == "img":
            previous.decompose()
        tag.name = "a"
        tag['resource'] = slug
        tag['href'] = ''
        del tag['id']
        tag.clear()
        tag

    with open(f"{out_dir}/scalar-pages.csv", 'w', newline='', encoding='utf-8') as pagescsv:
        scalarfields = ['dcterms:title', 'scalar:slug', 'sioc:content']
        write = csv.DictWriter(pagescsv, fieldnames=scalarfields, delimiter=',')
        write.writeheader()
        for h1 in soup.find_all('h1'):
            contents = []
            for sibling in h1.next_siblings:
                if sibling.name == 'h1':
                    break
                else:
                    if sibling.string == '\n':
                        continue
                    else:
                        contents.append(sibling)
            page = ''.join(str(x) for x in contents)
            write.writerow({'dcterms:title': h1.contents[0], 'scalar:slug': h1['id'], 'sioc:content': page})


def api_media(man_file, out_dir, isbn, media_dir, process_opt, handle, email, password):
    """Convert docx file to Scalar formatted CSV and submit media to a DSpace instance through a REST API."""
    html_man = f"./{out_dir}/temp/manuscript.html"
    if media_dir:
        sub_dir = shutil.copytree(media_dir, f'{out_dir}/temp/media')
        pypandoc.convert_file(man_file, 'html', format='docx', outputfile=html_man)
    else:
        pypandoc.convert_file(man_file, 'html', format='docx',
                              extra_args=[f'--extract-media=./{out_dir}/temp'], outputfile=html_man)
    with open(html_man, encoding='utf-8') as man:
        soup = BeautifulSoup(man, 'html.parser')
    inventory = f'./{out_dir}/temp/SAFinventory.csv'
    media = []
    for tag in soup.find_all('h6'):
        filename = tag.contents[0].split(' | ')[0].lower()
        try:
            source = tag.contents[0].split(' | ')[1]
        except:
            source = 'unknown'
        description = os.path.splitext(filename)[0]
        slug = f"{description}-draft"
        previous = tag.find_previous("p")
        if previous.contents[0].name == "img":
            try:
                path = previous.img['src']
                src = os.path.split(path)[1]
            except:
                src = ''
            try:
                alt = previous.img['alt']
            except:
                alt = ''
            previous.decompose()
        else:
            src = ''
            alt = ''
        media.append({'dc.title': slug, 'dc.description': description, 'dcterms.source': source,
                      'dcterms.abstract': alt, 'rs.originalFile': filename, 'file': src})
        tag.name = "a"
        tag['resource'] = slug
        tag['href'] = ''
        del tag['id']
        tag.clear()
        tag

    s = set()
    for item in media:
        s.add(item['dc.title'])
    seriesNum = 1
    for title in s:
        for item in media:
            if item['dc.title'] == title:
                item['dcterms.identifier'] = f"{isbn}_{seriesNum:03}"
                item['dc.title'] = f'{item["dcterms.identifier"]}-draft'
                if media_dir:
                    ext = os.path.splitext(item['rs.originalFile'])[1]
                    old_fn = item['rs.originalFile']
                    new_fn = f'{item["dcterms.identifier"]}{ext}'
                else:
                    ext = os.path.splitext(item['file'])[1]
                    old_fn = item['file']
                    new_fn = f'{item["dcterms.identifier"]}_P{ext}'
                os.renames(f'./{out_dir}/temp/media/{old_fn}', f'./{out_dir}/temp/media/{new_fn}')
                seriesNum += 1
                break

    if media_dir:
        with os.scandir(sub_dir) as it:
            for entry in it:
                if not entry.name.startswith(isbn) and entry.is_file():
                    identifier = f'{isbn}_{seriesNum:03}'
                    filename = os.path.splitext(entry.name)[0]
                    ext = os.path.splitext(entry.name)[1]
                    media.append({'dc.title': f'{identifier}-draft', 'dc.description': filename,
                                  'dcterms.identifier': identifier, 'dcterms.source': "unknown", 'dcterms.abstract': '',
                                  'rs.originalFile': entry.name, 'file': ''})
                    os.renames(f'{sub_dir}/{entry.name}', f'{sub_dir}/{identifier}{ext}')
                    seriesNum += 1

        if process_opt == 1:
            pass
        elif process_opt == 2:
            fileProcessing.fileConversions(sub_dir)
        elif process_opt == 3:
            fileProcessing.fileOptimizations(sub_dir)

    for item in media:
        if 'dcterms.identifier' in item:
            identifier = item['dcterms.identifier']
            optfiles = []
            with os.scandir(f'./{out_dir}/temp/media') as it:
                for entry in it:
                    if entry.name.startswith(identifier):
                        optfiles.append(entry.name)
            filenames = "|".join(optfiles)
            item['file'] = filenames
            for optfile in optfiles:
                filen = os.path.splitext(optfile)[0]
                if filen.endswith('_M'):
                    pass
                elif filen.endswith('_TH'):
                    item['rs.thumbFile'] = optfile
                else:
                    item['rs.streamFile'] = optfile

    with open(inventory, 'w', newline='') as dspacecsv:
        mediafields = ['dc.title', 'dc.description', 'dcterms.abstract', 'dcterms.identifier', 'dcterms.source',
                       'rs.originalFile', 'rs.streamFile', 'rs.thumbFile', 'file']
        mediaWrite = csv.DictWriter(dspacecsv, fieldnames=mediafields, delimiter=',')
        mediaWrite.writeheader()
        for item in media:
            if 'dcterms.identifier' in item:
                mediaWrite.writerow(item)
            else:
                pass

    with open(f"./{out_dir}/scalar-pages.csv", 'w', newline='', encoding='utf-8') as pagescsv:
        scalarfields = ['dcterms:title', 'scalar:slug', 'sioc:content']
        write = csv.DictWriter(pagescsv, fieldnames=scalarfields, delimiter=',')
        write.writeheader()
        for h1 in soup.find_all('h1'):
            contents = []
            for sibling in h1.next_siblings:
                if sibling.name == 'h1':
                    break
                else:
                    if sibling.string == '\n':
                        continue
                    else:
                        contents.append(sibling)
            page = ''.join(str(x) for x in contents)
            write.writerow({'dcterms:title': h1.contents[0], 'scalar:slug': h1['id'], 'sioc:content': page})

    baseURL = 'https://media.ravenspacepublishing.org'
    jsonFile = f"./{out_dir}/temp/metadataNewFiles.json"
    createItemMetadataFromCSV.convert(inventory, jsonFile)

    fileList = {}
    for root, dirs, files in os.walk(f'./{out_dir}/temp/media', topdown=True):
        for file in files:
            fullFilePath = os.path.join(root, file).replace('\\', '/')
            fileList[file] = fullFilePath

    f = csv.writer(open(f'./{out_dir}/temp/' + handle.replace('/', '-') + 'addedFilesList.csv', 'w', newline=''))
    f.writerow(['itemID'])

    for k, v in fileList.items():
        f.writerow([v[v.rindex('/') + 1:]])
    counter = len(fileList)

    data = {'email': email, 'password': password}
    header = {'content-type': 'application/json', 'accept': 'application/json'}
    session = requests.post(baseURL + '/rest/login', headers=header, verify=True,
                            params=data).cookies['JSESSIONID']
    cookies = {'JSESSIONID': session}

    status = requests.get(baseURL
                          + '/rest/status', headers=header,
                          cookies=cookies, verify=True).json()
    userFullName = status['fullname']
    print('authenticated', userFullName)
    headerFileUpload = {'accept': 'application/json'}

    # Get collection ID
    endpoint = baseURL + '/rest/handle/' + handle
    collection = requests.get(endpoint, headers=header, cookies=cookies,
                              verify=True).json()
    collectionID = str(collection['uuid'])
    print(collectionID)

    # Post items
    collectionMetadata = json.load(open(f'./{out_dir}/temp/metadataNewFiles.json'))
    with open(f'{out_dir}/scalar-media.csv', 'w', encoding='utf-8', newline='') as mediacsv:
        scalarMediaFields = ['dcterms:title', 'dcterms:description', 'dcterms:source', 'dcterms:abstract',
                             'dcterms:identifier', 'scalar:slug', 'art:url', 'art:thumbnail']
        writer = csv.DictWriter(mediacsv, fieldnames=scalarMediaFields)
        writer.writeheader()
        for itemMetadata in collectionMetadata:
            counter = counter - 1
            print('Items remaining: ', counter)
            fileExists = ''
            updatedItemMetadata = {}
            scalarElements = {}
            updatedItemMetadataList = []
            for element in itemMetadata['metadata']:
                if element['key'] == 'fileIdentifier':
                    fileIdentifier = element['value']
                elif element['key'] == 'dc.title':
                    scalarElements['dcterms:title'] = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'dcterms.source':
                    scalarElements['dcterms:source'] = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'dcterms.abstract':
                    scalarElements['dcterms:abstract'] = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'dcterms.identifier':
                    itemIdentifier = element['value']
                    scalarElements['dcterms:identifier'] = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'dc.description':
                    scalarElements['dcterms:description'] = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'rs.originalFile':
                    ofilename = element['value']
                    name = os.path.splitext(ofilename)[0]
                    slug = f'{name}-draft'
                    scalarElements['scalar:slug'] = slug
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'rs.streamFile':
                    streamFile = element['value']
                    updatedItemMetadataList.append(element)
                elif element['key'] == 'rs.thumbFile':
                    thumbFile = element['value']
                    updatedItemMetadataList.append(element)
                else:
                    updatedItemMetadataList.append(element)
            updatedItemMetadata['metadata'] = updatedItemMetadataList
            updatedItemMetadata = json.dumps(updatedItemMetadata)
            for k in fileList:
                if fileIdentifier in k:
                    fileExists = True
            if fileExists is True:
                print(fileIdentifier)
                post = requests.post(baseURL + '/rest/collections/' + collectionID
                                     + '/items', headers=header, cookies=cookies,
                                     verify=True, data=updatedItemMetadata).json()
                print(json.dumps(post))
                itemID = post['link']
                scalarElements['art:url'] = f"{baseURL}/jspui/html/{post['handle']}/{streamFile}"
                try:
                    scalarElements['art:thumbnail'] = f"{baseURL}/jspui/html/{post['handle']}/{thumbFile}"
                except UnboundLocalError:
                    # Switch to default fallback thumbnail file
                    scalarElements['art:thumbnail'] = ''

            orderedFileList = collections.OrderedDict(sorted(fileList.items()))
            for k, v in orderedFileList.items():
                if k.startswith(itemIdentifier):
                    bitstream = orderedFileList[k]
                    fileName = bitstream[bitstream.rfind('/') + 1:]
                    print(fileName)
                    data = open(bitstream, 'rb')
                    post = requests.post(baseURL + itemID + '/bitstreams?name='
                                         + fileName, headers=headerFileUpload,
                                         cookies=cookies, verify=True,
                                         data=data).json()
                    print(post)

            writer.writerow(scalarElements)

    logout = requests.post(baseURL + '/rest/logout', headers=header,
                           cookies=cookies, verify=True)
    print('Logged Out')


def saf_media(man_file, out_dir, isbn, media_dir, process_opt):
    html_man = f"./{out_dir}/temp/manuscript.html"
    if media_dir:
        sub_dir = shutil.copytree(media_dir, f'{out_dir}/temp/media')
        pypandoc.convert_file(man_file, 'html', format='docx', outputfile=html_man)
    else:
        pypandoc.convert_file(man_file, 'html', format='docx',
                              extra_args=[f'--extract-media=./{out_dir}/temp'], outputfile=html_man)
    with open(html_man, encoding='utf-8') as man:
        soup = BeautifulSoup(man, 'html.parser')
    inventory = f'./{out_dir}/temp/SAFinventory.csv'
    media = []
    for tag in soup.find_all('h6'):
        filename = tag.contents[0].split(' | ')[0].lower()
        try:
            source = tag.contents[0].split(' | ')[1]
        except:
            source = 'unknown'
        description = os.path.splitext(filename)[0]
        slug = f"{description}-draft"
        previous = tag.find_previous("p")
        if previous.contents[0].name == "img":
            try:
                path = previous.img['src']
                src = os.path.split(path)[1]
            except:
                src = ''
            try:
                alt = previous.img['alt']
            except:
                alt = ''
            previous.decompose()
        else:
            src = ''
            alt = ''
        media.append({'dc.title': slug, 'dc.description': description, 'dcterms.source': source,
                      'dcterms.abstract': alt, 'rs.originalFile': filename, 'file': src})
        tag.name = "a"
        tag['resource'] = slug
        tag['href'] = ''
        del tag['id']
        tag.clear()
        tag

    s = set()
    for item in media:
        s.add(item['dc.title'])
    seriesNum = 1
    for title in s:
        for item in media:
            if item['dc.title'] == title:
                item['dcterms.identifier'] = f"{isbn}_{seriesNum:03}"
                item['dc.title'] = f'{item["dcterms.identifier"]}-draft'
                if media_dir:
                    ext = os.path.splitext(item['rs.originalFile'])[1]
                    old_fn = item['rs.originalFile']
                    new_fn = f'{item["dcterms.identifier"]}{ext}'
                else:
                    ext = os.path.splitext(item['file'])[1]
                    old_fn = item['file']
                    new_fn = f'{item["dcterms.identifier"]}_P{ext}'
                os.renames(f'./{out_dir}/temp/media/{old_fn}', f'./{out_dir}/temp/media/{new_fn}')
                seriesNum += 1
                break

    if media_dir:
        with os.scandir(sub_dir) as it:
            for entry in it:
                if not entry.name.startswith(isbn) and entry.is_file():
                    identifier = f'{isbn}_{seriesNum:03}'
                    filename = os.path.splitext(entry.name)[0]
                    ext = os.path.splitext(entry.name)[1]
                    media.append({'dc.title': f'{identifier}-draft', 'dc.description': filename,
                                  'dcterms.identifier': identifier, 'dcterms.source': "unknown", 'dcterms.abstract': '',
                                  'rs.originalFile': entry.name, 'file': ''})
                    os.renames(f'{sub_dir}/{entry.name}', f'{sub_dir}/{identifier}{ext}')
                    seriesNum += 1

        if process_opt == 1:
            pass
        elif process_opt == 2:
            fileProcessing.fileConversions(sub_dir)
        elif process_opt == 3:
            fileProcessing.fileOptimizations(sub_dir)

    for item in media:
        if 'dcterms.identifier' in item:
            identifier = item['dcterms.identifier']
            optfiles = []
            with os.scandir(f'./{out_dir}/temp/media') as it:
                for entry in it:
                    if entry.name.startswith(identifier):
                        optfiles.append(entry.name)
            filenames = "|".join(optfiles)
            item['file'] = filenames
            for optfile in optfiles:
                filen = os.path.splitext(optfile)[0]
                if filen.endswith('_M'):
                    pass
                elif filen.endswith('_TH'):
                    item['rs.thumbFile'] = optfile
                else:
                    item['rs.streamFile'] = optfile

    with open(inventory, 'w', newline='') as dspacecsv:
        mediafields = ['dc.title', 'dc.description', 'dcterms.abstract', 'dcterms.identifier', 'dcterms.source',
                       'rs.originalFile', 'rs.streamFile', 'rs.thumbFile', 'file']
        mediaWrite = csv.DictWriter(dspacecsv, fieldnames=mediafields, delimiter=',')
        mediaWrite.writeheader()
        for item in media:
            if 'dcterms.identifier' in item:
                mediaWrite.writerow(item)
            else:
                pass

    with open(f"./{out_dir}/scalar-pages.csv", 'w', newline='', encoding='utf-8') as pagescsv:
        scalarfields = ['dcterms:title', 'scalar:slug', 'sioc:content']
        write = csv.DictWriter(pagescsv, fieldnames=scalarfields, delimiter=',')
        write.writeheader()
        for h1 in soup.find_all('h1'):
            contents = []
            for sibling in h1.next_siblings:
                if sibling.name == 'h1':
                    break
                else:
                    if sibling.string == '\n':
                        continue
                    else:
                        contents.append(sibling)
            page = ''.join(str(x) for x in contents)
            write.writerow({'dcterms:title': h1.contents[0], 'scalar:slug': h1['id'], 'sioc:content': page})

    arc_dir = f'./{out_dir}/temp/archives'
    sub_dir = f'./{out_dir}/temp/media'
    SimpleArchiveBuilder.run(out_dir, sub_dir, arc_dir, inventory)
