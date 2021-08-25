import json
import csv


def createMetadataElementCSV(key, valueSource, language, metadata):
    """Create metadata element."""
    value = valueSource
    if value != '':
        if language != '':
            metadataElement = {'key': key, 'language': language,
                               'value': value}
            metadata.append(metadataElement)
        else:
            metadataElement = {'key': key, 'value': value}
            metadata.append(metadataElement)
    else:
        pass


def createMetadataElementCSVSplitField(key, valueSource, language, metadata):
    """Create multiple metadata elements from one field."""
    if valueSource != '':
        if '|' in valueSource:
            values = valueSource.split('|')
            for value in values:
                if language != '':
                    metadataElement = {'key': key, 'language': language,
                                       'value': value}
                    metadata.append(metadataElement)
                else:
                    metadataElement = {'key': key, 'value': value}
                    metadata.append(metadataElement)
        else:
            value = valueSource
            if language != '':
                metadataElement = {'key': key, 'language': language,
                                   'value': value}
                metadata.append(metadataElement)
            else:
                metadataElement = {'key': key, 'value': value}
                metadata.append(metadataElement)
    else:
        pass


def createMetadataElementDirect(key, value, language):
    """Create metadata element with specified value."""
    if language != '':
        metadataElement = {'key': key, 'language': language, 'value': value}
        metadata.append(metadataElement)
    else:
        metadataElement = {'key': key, 'value': value}
        metadata.append(metadataElement)


def convert(fileName, jsonFile):
    with open(fileName) as csvfile:
        reader = csv.DictReader(csvfile)
        counter = 0
        metadataGroup = []
        for row in reader:
            metadata = []
            createMetadataElementCSVSplitField('fileIdentifier', row['file'], '', metadata)
            createMetadataElementCSV('dc.title', row['dc.title'], '', metadata)
            createMetadataElementCSV('dc.description', row['dc.description'], '', metadata)
            createMetadataElementCSV('dcterms.identifier', row['dcterms.identifier'], '', metadata)
            createMetadataElementCSV('dcterms.source', row['dcterms.source'], '', metadata)
            createMetadataElementCSV('dcterms.abstract', row['dcterms.abstract'], '', metadata)
            createMetadataElementCSV('rs.originalFile', row['rs.originalFile'], '', metadata)
            createMetadataElementCSV('rs.streamFile', row['rs.streamFile'], '', metadata)
            createMetadataElementCSV('rs.thumbFile', row['rs.thumbFile'], '', metadata)
            item = {'metadata': metadata}
            metadataGroup.append(item)
            counter = counter + 1
            print(counter)

    f = open(jsonFile, 'w')
    json.dump(metadataGroup, f)


if __name__ == '__main__':
    fileName = input('Enter fileName (including \'.csv\'): ')
    jsonFile = "metadata.json"
    convert(fileName, jsonFile)
