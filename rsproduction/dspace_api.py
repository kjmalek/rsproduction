import os
import csv
import json
import collections

import requests

from . import csv2metadata


def ingest(out_dir, csv_inv, handle, email, password):
    baseURL = 'https://media.ravenspacepublishing.org'
    jsonFile = f"{out_dir}/temp/metadataNewFiles.json"
    csv2metadata.convert(csv_inv, jsonFile)

    fileList = {}
    for root, dirs, files in os.walk(f'{out_dir}/temp/media', topdown=True):
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
    session = requests.post(baseURL + '/rest/login', headers=header, verify=True, params=data).cookies['JSESSIONID']
    cookies = {'JSESSIONID': session}

    status = requests.get(baseURL + '/rest/status', headers=header, cookies=cookies, verify=True).json()
    userFullName = status['fullname']
    print('authenticated', userFullName)
    headerFileUpload = {'accept': 'application/json'}

    # Get collection ID
    endpoint = baseURL + '/rest/handle/' + handle
    collection = requests.get(endpoint, headers=header, cookies=cookies, verify=True).json()
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
                post = requests.post(baseURL + '/rest/collections/' + collectionID + '/items', headers=header,
                                     cookies=cookies, verify=True, data=updatedItemMetadata).json()
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
                    post = requests.post(baseURL + itemID + '/bitstreams?name=' + fileName, headers=headerFileUpload,
                                         cookies=cookies, verify=True, data=data).json()
                    print(post)

            writer.writerow(scalarElements)

    logout = requests.post(baseURL + '/rest/logout', headers=header, cookies=cookies, verify=True)
    print('Logged Out')