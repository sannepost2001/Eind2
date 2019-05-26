import Bio
import mysql.connector
from time import sleep
# from tkinter import Tk, filedialog
from Bio.Blast.NCBIWWW import qblast
from Bio.Blast import NCBIXML
from Bio import Entrez
from Bio import SearchIO

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
        self.cursor = self.database.cursor(buffered=True)

    # def insert(self, table, cols, valuelist):
    #     self.database.commit()
    #     """Insert something into database
    #     :param table:
    #     :param cols:
    #     :param valuelist:
    #     """
    #     if isinstance(valuelist, str):
    #         query = "insert into {}({}) value({})".format(table, cols,
    #                                                       valuelist)
    #     else:
    #         query = "insert into {}({}) values({})".format(table, cols,
    #                                                      valuelist)
    #     self.cursor.execute(query)
    #     self.database.commit()
    # Omitted for ease of use

    def taxonomy(self, a_acode):
        """Function for retrieving taxonomy data from the NCBI-taxonomy
        database
        :param a_acode: accession code recorded in a hsp
        :return: returns an ordered list containing the organisms taxonomy
        """
        search = Entrez.efetch(id=a_acode, db="protein", retmode="xml")
        data = Entrez.read(search)
        speciesname = data[0].get('GBSeq_organism')
        search = Entrez.esearch(term=speciesname, db="taxonomy", retmode="xml")
        record = Entrez.read(search)
        taxid = record['IdList'][0]
        search = Entrez.efetch(id=taxid, db="taxonomy", retmode="xml")
        data = Entrez.read(search)
        data = data[0].get('Lineage').split('; ')
        data.append(speciesname.split(" ")[1])
        return data

    def save_header(self, header):
        query = "insert into original(header) value('{}')".format(header)
        self.cursor.execute(query)
        self.database.commit()

    def save_sequence(self, seq, read, score):
        print(seq, read, score)
        self.cursor.execute("select max(id) from original")
        og_id = self.cursor.fetchone()[0]
        query = "insert into sequence(sequence, readnr, score, ORIGINAL_id)" \
                "values('{}', {}, {}, {})".format(seq, read, score, og_id)
        self.cursor.execute(query)
        self.database.commit()

    def save_blast(self, filename, seq_id):
        """Insert all data into database
        :param header: Header to insert
        :param read: Read to insert
        :param seq: Sequence to insert
        :param score: FASTQ score to insert
        :param blast_results: Rest of data to insert as BLAST XML results
        """
        result_handle = open(filename, "r")
        blast_records = NCBIXML.parse(result_handle)

        for blast_record in blast_records:
            print("checkpoint")
            # Todo: create method for saving taxonomy data AND recreate blast insert
            # for a, alignment in enumerate(blast_record.alignments):
            #     if a == 10:
            #         print("10 results")
            #         return None
            #
            #     title = alignment.title.split("|")
            #     a_name = title[2]  # Example title: >gb|AF283004.1|AF283004 Arabidopsis thaliana etc etc
            #     a_acode = title[1]
            #     tax_list = self.taxonomy(a_acode)
            #     desc = blast_record.descriptions[a].title
            #     for tax in tax_list:
            #         self.cursor.execute("select id from taxonomy where "
            #                             "name='{}'".format(tax))
            #         tax_id = self.cursor.fetchone()[0]
            #         if not tax_id:
            #             query = "insert into taxonomy(name) " \
            #                     "value('{}')".format(tax)
            #             self.cursor.execute(query)
            #         else:
            #             query = "insert into taxonomy(name, TAXONOMY_id) " \
            #                     "values('{}', {})".format(tax, tax_id)
            #             self.cursor.execute(query)
            #
            #     for i, hsp in enumerate(alignment.hsps):  # Limit to 10 results?
            #         columns = "name, accessioncode, description, maxscore, " \
            #                   "bits, evalue, querycoverage, percidentity, " \
            #                   "SEQUENCE_id, TAXONOMY_id"
            #         values = ("'" + a_name + "'", "'" + a_acode + "'",
            #                   "'" + desc + "'", hsp.score, float(hsp.bits),
            #                   hsp.expect, (hsp.query-hsp.query_start)/300,
            #                   hsp.identity, seq_id, tax_id)
            #         self.insert("blast", columns, values)

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
        self.blastmethod = "blastx"

    def blast(self, filename, seq, seq_id):
        """
        Put a sequence in BLAST
        :param seq: Sequence to use
        :return: Returns BLAST results
        """
        result_handle = qblast(self.blastmethod, self.database, seq,
                        format_type=self.format, expect=self.evalue,
                        matrix_name=self.matrix)
        file = open(filename, "w+")
        result_xml = result_handle.readlines()
        file.writelines(result_xml)
        file.close()





def main():
    file = "Course4_dataset_v03.tsv"

    readfile(file)
    print("Script done")


def readfile(data_file):
    """
    :param data_file:
    :return:
    """
    db = Database()
    blast = BLASTer()
    i = 0
    db.cursor.execute("select count(sequence) from sequence")
    count = db.cursor.fetchone()[0]
    if count != 200:
        with open(data_file, "r") as file:
            for line in file:
                i += 1
                content = line.split("\t")
                header = content[0][:-2]
                db.save_header(header)
                print("header saved")

                read = content[0][-1:]
                score = calc_score(content[2])
                seq = content[1]
                db.save_sequence(seq, read, score)
                print("sequence saved")
                i += 1
                read = content[3][-1:]
                seq = content[4]
                score = calc_score(content[5])
                db.save_sequence(seq, read, score)
                print("sequence saved")
    else:
        db.cursor.execute("select sequence from sequence")
        sequences = db.cursor.fetchall()
        for sequence in sequences:
            BLAST(sequence[0])


def BLAST(seq):
    db = Database()
    toblast = BLASTer()
    db.cursor.execute("select id from sequence where sequence='{}'".format(seq))
    seq_id = db.cursor.fetchone()[0]
    filename = "results_blast_{}.xml".format(seq_id)
    print("blasting")
    records = toblast.blast(filename, seq, seq_id)
    print("blast complete")

    db.save_blast(filename, seq_id)
    print("blast saved")
    print("Pausing 3 min")
    sleep(180)


def calc_score(score):
    """transcribes the FASTQ score string to an integer and returns
    :param score: FASTQ score string from provided tsv file
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