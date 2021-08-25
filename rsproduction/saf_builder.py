import xml.etree.ElementTree as ET
import csv
import os.path
import io
from os.path import normpath
from os import makedirs
from shutil import copyfile, make_archive, rmtree


class BOAS_CSV_IMPORT:
    def __init__(self, out_dir, sub_dir, arc_dir):
        self.filepath = normpath(sub_dir)
        self.exportpath = normpath(arc_dir)
        makedirs(self.exportpath)
        self.archivepath = normpath(f'./{out_dir}/archive')
        rmtree(self.exportpath)

    def make_dc(self, line):
        root = ET.Element('dublin_core')
        pairs = line.items()
        for key, value in pairs:
            term_parts = key.split('dc.')
            if len(term_parts) > 1 and value:
                ET.SubElement(root, 'dcvalue', element=term_parts[1], qualifier='none').text = value
        bytes = ET.tostring(root, encoding="utf-8", method="xml")
        return bytes.decode("utf-8")
    
    def make_dcterms(self, line):
        root = ET.Element('dublin_core', schema="dcterms")
        pairs = line.items()
        for key, value in pairs:
            term_parts = key.split('dcterms.')
            if len(term_parts) > 1 and value:
                ET.SubElement(root, 'dcvalue', element=term_parts[1], qualifier='none').text = value
        bytes = ET.tostring(root, encoding="utf-8", method="xml")
        return bytes.decode("utf-8")
    
    def make_rs(self, line):
        root = ET.Element('dublin_core', schema="rs")
        pairs = line.items()
        for key, value in pairs:
            term_parts = key.split('rs.')
            if len(term_parts) > 1 and value:
                ET.SubElement(root, 'dcvalue', element=term_parts[1], qualifier='none').text = value
        bytes = ET.tostring(root, encoding="utf-8", method="xml")
        return bytes.decode("utf-8")

    def make_vra(self, line):
        root = ET.Element('dublin_core', schema="vra")
        pairs = line.items()
        for key, value in pairs:
            term_parts = key.split('vra.')
            if len(term_parts) > 1 and value:
                ET.SubElement(root, 'dcvalue', element=term_parts[1], qualifier='none').text = value
        bytes = ET.tostring(root, encoding="utf-8", method="xml")
        return bytes.decode("utf-8")

    def harvest(self, inventory):
        with io.open(normpath(inventory), encoding='utf8') as file:
            d_reader = csv.DictReader(file)
            for line in d_reader:
                dublic_core = self.make_dc(line)
                dcterms = self.make_dcterms(line)
                rs = self.make_rs(line)
                vra = self.make_vra(line)
                identifier = line['dc.title']
                folder = identifier
                export_dir = "{0}/{1}/".format(self.exportpath, folder)
                export_dir = normpath(export_dir)
                if not os.path.exists(export_dir):
                    makedirs(export_dir)
                dc_file_path = normpath(export_dir + '/dublin_core.xml')
                dc_file = io.open(dc_file_path, 'w', encoding='utf8')
                dc_file.write(dublic_core)
                dc_file.close()
                dcterms_file_path = normpath(export_dir + '/metadata_dcterms.xml')
                dcterms_file = io.open(dcterms_file_path, 'w', encoding='utf8')
                dcterms_file.write(dcterms)
                dcterms_file.close()
                rs_file_path = normpath(export_dir + '/metadata_rs.xml')
                rs_file = io.open(rs_file_path, 'w', encoding='utf8')
                rs_file.write(rs)
                rs_file.close()
                vra_file_path = normpath(export_dir + '/metadata_vra.xml')
                vra_file = io.open(vra_file_path, 'w', encoding='utf8')
                vra_file.write(vra)
                vra_file.close()
                files = line['file'].split("|")
                for file in files:
                    asset = normpath("{0}/{1}".format(self.filepath, file))
                    copyfile(asset, normpath("{0}/{1}".format(export_dir, file)))
                with open(normpath("{0}/contents".format(export_dir)), 'w') as contents_file:
                    for file in files:
                        contents_file.write(f"{file}\n")
        make_archive(self.archivepath, 'zip', self.exportpath)


def run(out_dir, sub_dir, arc_dir, inventory):
    print("Packaging files and metadata into Simple Archive Format...")
    migrate = BOAS_CSV_IMPORT(out_dir, sub_dir, arc_dir)
    migrate.harvest(inventory)
    print("Done. The zip drive, archive.zip, is ready to be uploaded to DSpace.")
