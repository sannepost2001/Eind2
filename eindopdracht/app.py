# Sanne Post
# 18-5-19
# Website champignon compost
import mysql.connector
from Bio.Blast import NCBIWWW, NCBIXML
from flask import Flask, request, render_template, make_response
# tijdelijke imports
import sys
import traceback
app = Flask(__name__)


@app.route('/')
def home():
    """ Opent de home pagina
    """
    resp = make_response(render_template('home.html'))
    return resp


@app.route('/<path:filename>', methods=['GET', 'POST'])
def pagina(filename):
    """ Opent de pagina als er op geklikt wordt.
    input: templtes en de pagina die aangeklikt is op de bestaande pagina en zoekdata als die nodig zijn
    output: weergave van de uitgekozen pagina en de data die hoort bij de zoekdata
    """
    if filename == "bacterie.html":
        # """ Als er op zoeken op bacterie naam wordt gebruikt dan wordt de bacterie.html pagina aangeroepen.
        # deze pagina moet nog aangevuld worden met de data die je kruigt als je filterd op het zoekword
        # """

        searchword = ""
        zoekwoord = ""
        teruggeven = ""
        giveback = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                           user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                           password="ConnectionPWD")
            cursor = conn.cursor()

            try:
                zoekwoord = request.form["zoekwoord"]
            except KeyError:
                zoekwoord = ""

            try:
                searchword = request.form["searchword"]
            except KeyError:
                searchword = ""

            if zoekwoord != "":
                # Query die zoekt op het zoekwoord
                sql = "select blast.name, blast.accessioncode, functionality.function from " \
                      "blast left join functionint on blast.id = functionint.BLAST_id " \
                      "left join functionality on functionint.functionality_id = functionality.id " \
                      "where blast.name like '%" + zoekwoord + "%'"
                cursor.execute(sql)

                records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
                print(records)
                teruggeven = ("<p2>Gevonden data van het zoeken op protiën naam:</p2><br>\n"
                              + "<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                              + "   <tr>\n"
                              + "   <th onclick=\"sortTable(0)\">Naam</th>\n"
                              + "   <th onclick=\"sortTable(1)\">Accessiecode:</th>\n"
                              + "   <th onclick=\"sortTable(2)\">Functie:</th>\n"
                              + "   </tr>")
                for row in records:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td>" + str(row[0]) + "</td>"
                    teruggeven = teruggeven + "<td>" + str(row[1]) + "</td>"
                    teruggeven = teruggeven + "<td>" + str(row[2]) + "</td>"
                    teruggeven = teruggeven + "</tr>"
                teruggeven = teruggeven + "</table>"
            if searchword != "":
                sql = "select blast.accessioncode, blast.name, taxonomy.name from taxonomy join blast on blast.TAXONOMY_id = taxonomy.id join taxonomy b on b.TAXONOMY_id = taxonomy.id where taxonomy.name like'%" + searchword + "%'"
                cursor.execute(sql)
                data = cursor.fetchall()
                cursor.close()
                conn.close()
                # maakt een tabel van de gevonden data
                giveback = ("<p2>Gevonden data van het zoeken op taxonomy:</p2><br>\n"
                            + "<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                            + "   <tr>\n"
                            + "   <th onclick=\"sortTable(0)\">Accessiecode</th>\n"
                            + "   <th onclick=\"sortTable(1)\">Naam</th>\n"
                            + "   <th onclick=\"sortTable(2)\">Taxonomy</th>\n"
                            + "   </tr>")

                for a in data:
                    giveback = giveback + "<tr>"
                    giveback = giveback + "<td>" + str(a[0]) + "</td>"
                    giveback = giveback + "<td>" + str(a[1]) + "</td>"
                    giveback = giveback + "<td>" + str(a[2]) + "</td>"
                    giveback = giveback + "</tr>"

                giveback = giveback + "</table>"

        return render_template("bacterie.html", teruggeven=teruggeven, zoekwoord=zoekwoord, giveback=giveback,
                               searchword=searchword)


    elif filename == "tabel.html":
        """"""
        # try:
        teruggeven = ""
        sql = ""
        naam = ""
        coverage = ""
        score = ""
        identity = ""
        evalue = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                           user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                           password="ConnectionPWD")
            cursor = conn.cursor()
            naam = request.form["naam"]
            coverage = request.form["coverage"]
            score = request.form["score"]
            identity = request.form["identity"]
            evalue = request.form["evalue"]
            if naam != "":
                #
                sql = sql + " and blast.name like '%" + naam + "%'"
            if coverage != "":
                #
                sql = sql + " and querycoverage > " + coverage
            if score != "":
                #
                sql = sql + " and bits > " + score
            if identity != "":
                #
                sql = sql + " and percidentity > " + identity
            if evalue != "":
                #
                sql = sql + " and evalue < " + evalue + "%'"
            #
            query = "select blast.name, evalue, bits, querycoverage, percidentity from blast where 1=1" + sql
            cursor.execute(query)
            records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
            cursor.close()
            conn.close()
            teruggeven = ("<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "    <tr>\n"
                          + "    <th onclick=\"sortTable(0)\">Naam</th>\n"
                          + "    <th onclick=\"sortTable(1)\">E-value:</th>\n"
                          + "    <th onclick=\"sortTable(2)\">(Bit)score:</th>\n"
                          + "    <th onclick=\"sortTable(3)\">Coverage:</th>\n"
                          + "    <th onclick=\"sortTable(4)\">%identity:</th>\n"
                          + "    </tr>")
            for row in records:
                teruggeven = teruggeven + "<tr>"
                teruggeven = teruggeven + "<td>" + str((row[0])) + "</td>"
                teruggeven = teruggeven + "<td>" + str((row[1])) + "</td>"
                teruggeven = teruggeven + "<td>" + str((row[2])) + "</td>"
                teruggeven = teruggeven + "<td>" + str((row[3])) + "</td>"
                teruggeven = teruggeven + "<td>" + str((row[4])) + "</td>"
                teruggeven = teruggeven + "</tr>"
            teruggeven = teruggeven + "</table>"
        return (render_template("tabel.html", teruggeven=teruggeven, naam=naam, identity=identity, score=score,
                                evalue=evalue, coverage=coverage))
        # except:
        #     teruggeven = "Verkeerde zoek opdracht ingegeven. " + "<br>" + \
        #                  "Vul alleen bij de naam een woord in en bij de rest alleen getallen."
        #     return render_template("tabel.html", teruggeven=teruggeven)
    elif filename == "statistiek.html":
        # """"""
        # try:
        conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                       user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                       password="ConnectionPWD")
        cursor = conn.cursor()
        cursor.execute("select name, count(*) from blast group by name order by 2 desc limit 5")
        records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
        cursor.close()
        conn.close()
        teruggeven = "['Naam', '%'],"
        #
        for row in records:
            teruggeven = teruggeven + "['" + str(row[0]) + "', " + str(row[1]) + " ],"
        teruggeven = teruggeven[:-1]
        return render_template("statistiek.html", teruggeven=teruggeven)
    elif filename == "zelfblast.html":
        seq = ""
        teruggeven = ""
        if request.method == 'POST':
            try:
                seq = request.form["iets"]
            except Exception as err:
                seq = "Geef sequentie in"
            print(seq)
            if seq is not None:
                result_handle = NCBIWWW.qblast("blastx", "nr", seq)
                blast_records = NCBIXML.parse(result_handle)
                blast_record = next(blast_records)
                teruggeven = "<br>"
                for alignment in blast_record.alignments:
                    for hsp in alignment.hsps:
                        teruggeven = teruggeven + '---------------------------------'
                        teruggeven = teruggeven + 'sequence: ' + alignment.title
                        teruggeven = teruggeven + 'lengte: ' + alignment.length
                        teruggeven = teruggeven + 'e-value' + hsp.expect
                        teruggeven = teruggeven + hsp.query
                        teruggeven = teruggeven + hsp.match
                        teruggeven = teruggeven + hsp.sbjct
                if teruggeven == "<br>":
                    teruggeven = teruggeven + "Geen blast resultaten"
                print(teruggeven)
        return render_template("zelfblast.html", teruggeven=teruggeven, seq=seq)
    else:
        resp = make_response(render_template(filename))
        print("else")
        return resp





if __name__ == '__main__':
    app.run()
