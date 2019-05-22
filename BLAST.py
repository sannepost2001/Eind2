import Bio
import mysql.connector
from time import sleep
# from tkinter import Tk, filedialog
from Bio.Blast.NCBIWWW import qblast
from Bio.Blast import NCBIXML

# # #   To-do list
# Insert statements - Data from BLAST objects
# Insert statements - foreign keys?
# Taxonomy code/biopython calls
# "Resume after interrupted" code
# Save the XML blast result (Done?)


class Database:
    def __init__(self):
        host = "hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com"
        user = "kxxxf@hannl-hlo-bioinformatica-mysqlsrv"
        passw = "ConnectionPWD"
        dbname = "kxxxf"
        self.database = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)
        self.cursor = self.database.cursor()

    def insert(self, table, cols, valuelist):
        """Insert something into database"""
        vals = ""
        for value in valuelist:
            vals += value
        query = "insert into " + table + "(" + cols + ") values (" + vals + ")"
        self.cursor.execute(query)
        self.database.commit()

    def save_all(self, header, read, seq, blast_results):
        """Insert all data into database"""
        record = NCBIXML.parse(blast_results)
        # Todo: Read how to and make those loops reading every result

        columns = "header"
        values = [header]
        self.insert("original", columns, values)

        columns = "sequence, read, score"
        values = [seq, read, record.hsps.score]  # Todo: How does this work
        self.insert("sequence", columns, values)

        columns = "scale, name, TAXONOMY_id"
        values = []
        self.insert("taxonomy", columns, values)

        columns = "name, accessioncode, description, maxscore, bits, evalue, querycoverage, " \
                  "percidentity, SEQUENCE_id, TAXONOMY_id"  # Todo: Query and get right ID's?
        values = []
        self.insert("blast", columns, values)

        columns = "function"
        values = []
        self.insert("functionality", columns, values)

        columns = "FUNCTIONALITY_id, BLAST_id"
        values = []
        self.insert("functionint", columns, values)


class BLASTer:
    def __init__(self):
        self.seqs_blasted = 0  # Remember position in case BLAST blocks this (Unfinished feature)
        self.database = "nr"
        self.format = "XML"
        self.evalue = 0.04
        self.matrix = "BLOSUM62"
        self.blastmethods = ["blastx", "tblastx"]

    def blast(self, seq):
        for i, blastmethod in enumerate(self.blastmethods):
            result = qblast(self.blastmethods[i], self.database, seq, format_type=self.format,
                            expect=self.evalue, matrix_name=self.matrix)
            if result:
                self.seqs_blasted += 1
                return result


def main():
    file = "Course4_dataset_v03.csv"

    readfile(file)


def readfile(data_file):
    db = Database()
    blast = BLASTer()
    with open(data_file, "r") as file:
        for line in file:
            content = line.split("\t")
            header = content[0][:-2]
            read = content[0][-1:]
            seq = content[2]
            print("Checkpoint 1")  # Debug prints
            result = blast.blast(seq)
            print("Checkpoint 2")
            with open("blast results xml.xml", "w") as wfile:
                wfile.writelines(result)
            # db.save_all(header, read, seq, result)
            print("Pausing 3 min")
            sleep(180)

            header = content[4][:-2]
            read = content[4][-1:]
            seq = content[5]
            result = blast.blast(seq)
            # db.save_all(header, read, seq, result)
            sleep(180)


main()


""" Useful:
https://biopython.readthedocs.io/en/latest/Tutorial/chapter_blast.html#parsing-blast-output
"""