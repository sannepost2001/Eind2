import Bio
import mysql.connector
from time import sleep
# from tkinter import Tk, filedialog
from Bio.Blast.NCBIWWW import qblast
from Bio.Blast import NCBIXML
from Bio import Entrez

# # #   To-do list
# Insert statements - Data from BLAST objects (Done)
# Insert statements - foreign keys? (Done for sequence_id)
# Taxonomy code/biopython calls
# "Resume after interrupted" code


class Database:
    def __init__(self):
        host = "hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com"
        user = "kxxxf@hannl-hlo-bioinformatica-mysqlsrv"
        passw = "ConnectionPWD"
        dbname = "kxxxf"
        self.database = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)
        self.cursor = self.database.cursor()

    def insert(self, table, cols, valuelist):
        self.database.commit()
        """Insert something into database
        :param table:
        :param cols:
        :param valuelist:
        """
        vals = ""
        for value in valuelist:
            vals += value
        query = "insert into " + table + "(" + cols + ") values (" + vals + ")"
        self.cursor.execute(query)
        self.database.commit()

    def taxonomy(self, a_acode):
        search = Entrez.efetch(id=a_acode, db="protein", retmode="xml")
        data = Entrez.read(search)
        speciesname = data[0].get('GBSeq_organism')
        search = Entrez.esearch(term=speciesname, db="taxonomy",
                                retmode="xml")
        record = Entrez.read(search)
        taxid = record['IdList'][0]
        search = Entrez.efetch(id=taxid, db="taxonomy", retmode="xml")
        data = Entrez.read(search)
        data = data[0].get('Lineage').split('; ')
        data.append(speciesname.split(" ")[1])
        return data

    def save_all(self, header, read, seq, score, blast_results):
        """Insert all data into database
        :param header: Header to insert
        :param read: Read to insert
        :param seq: Sequence to insert
        :param score: FASTQ score to insert
        :param blast_results: Rest of data to insert as BLAST XML results
        """

        records = NCBIXML.parse(blast_results)

        columns = "header"
        values = [header]
        self.insert("original", columns, values)

        columns = "sequence, read, score"  # FASTQ score
        values = [seq, read, score]
        self.insert("sequence", columns, values)
        seq_id = self.cursor.execute(int("select MAX(id) from sequence"))

        for blast_record in records:
            for a, alignment in enumerate(blast_record.alignments):
                title = alignment.title.split("|")
                a_name = title[2]  # Example title: >gb|AF283004.1|AF283004 Arabidopsis thaliana etc etc
                a_acode = title[1]
                tax_list = self.taxonomy(a_acode)
                desc = blast_record.descriptions[a].title
                for i, hsp in enumerate(alignment.hsps):  # Limit to 10 results?
                    if i == 10:
                        print("10 results inserted.")
                        return None

                    for tax in tax_list:
                        taxid = self.cursor.execute(int("select MAX(id) from taxonomy"))  # "Real" ID
                        columns = "name, TAXONOMY_id"  # Todo: Have to finish taxonomy script for this
                        values = [tax, taxid]
                        self.insert("taxonomy", columns, values)
                    tax_id = self.cursor.execute(int("select MAX(id) from taxonomy"))  # Use for later referencesS

                    columns = "name, accessioncode, description, maxscore, bits, evalue, querycoverage, " \
                              "percidentity, SEQUENCE_id, TAXONOMY_id"
                    values = [a_name, a_acode, desc, hsp.score, float(hsp.bits),
                              hsp.expect, ((hsp.query-hsp.query_start)/300), hsp.identity,
                              seq_id, tax_id]
                    self.insert("blast", columns, values)

                    # columns = "function"  # Todo: Leave for later? Use accession code to find.
                    # values = []
                    # self.insert("functionality", columns, values)

            # columns = "FUNCTIONALITY_id, BLAST_id"  # Todo: Also query for right ID's
            # values = []
            # self.insert("functionint", columns, values)


class BLASTer:
    def __init__(self):
        self.seqs_blasted = 0  # Remember position in case BLAST blocks this (Unfinished feature)
        self.database = "nr"
        self.format = "XML"
        self.evalue = 0.04
        self.matrix = "BLOSUM62"
        self.blastmethods = ["blastx", "tblastx"]

    def blast(self, seq):
        """
        Put a sequence in BLAST
        :param seq: Sequence to use
        :return: Returns BLAST results
        """
        for i, blastmethod in enumerate(self.blastmethods):
            result = qblast(self.blastmethods[i], self.database, seq,
                            format_type=self.format, expect=self.evalue,
                            matrix_name=self.matrix)
            if result:
                self.seqs_blasted += 1
                return result


def main():
    file = "Course4_dataset_v03.csv"

    readfile(file)
    print("Script done")


def readfile(data_file):
    """
    :param data_file:
    :return:
    """
    db = Database()
    blast = BLASTer()
    with open(data_file, "r") as file:
        tcount = 0
        for line in file:
            tcount += 1
            if tcount == 11:  # Remove later
                print("Testing limit reached, quitting")
                return None
            content = line.split("\t")
            header = content[0][:-2]
            read = content[0][-1:]
            score = calc_score(content[2])
            seq = content[1]
            print("Blasting")  # Debug prints
            result = blast.blast(seq)
            # result = debug_usexmlfile()  # Debug, remove later
            # return None                  # Debug, remove later
            print("Blast complete")
            with open("blast results xml 1.xml", "w") as wfile:
                wfile.writelines(result)
            # db.insert_all(header, read, seq, score, result)
            print("Pausing 3 min")
            sleep(180)

            header = content[3][:-2]
            read = content[3][-1:]
            seq = content[4]
            score = calc_score(content[5])
            print("Blasting")
            result = blast.blast(seq)
            print("Blast complete")
            with open("blast results xml 2.xml", "w") as wfile:
                wfile.writelines(result)
            # db.insert_all(header, read, seq, score result)
            sleep(180)


def debug_usexmlfile():  # Debug, remove later
    with open("blast results xml.xml", "r") as rfile:
        result = rfile.readlines()
        result = NCBIXML.parse(result)
        return result


def calc_score(score):
    """transcribes the FASTQ score string to an integer and returns
    :param score: FASTQ score string from provided csv file
    :return: calculated FASTQ score integer
    """
    count = 0
    scorelist = ["!", '"', "#", "$", "%", "&", "'", "(", ")", "*", "+", ","
                 , "-", ".", "/", "0", "1", "2", "3", "4", "5", "6", "7",
                 "8", "9", ":", ";", "<", "=", ">", "?", "@", "A", "B", "C"
                 , "D", "E", "F", "G", "H", "I", "J", "K"]
    for letter in score:
        for i in range(len(scorelist)):
            if letter == scorelist[i]:
                count += i
    return count


main()


""" Useful:
https://biopython.readthedocs.io/en/latest/Tutorial/chapter_blast.html#parsing-blast-output
"""