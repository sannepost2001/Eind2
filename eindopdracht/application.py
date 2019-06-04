# Sanne Post
# 18-5-19
# Website champignon compost
import mysql.connector
from Bio.Blast import NCBIWWW, NCBIXML
from flask import Flask, request, render_template, make_response


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

    def taxonomies(nameinput):
        """
        Display the taxonomy of something using the taxonomy table in the database.
        Besides parameters, requires active cursor and database connection.
        :param nameinput: Name to get taxonomy for
        :return: Returns a string displaying taxonomy or an error
        """
        # nameinput = request.args.get("nameinput")
        cursor.execute("select id from taxonomy where name like '%" + nameinput + "%' limit 1")
        tax_id = cursor.fetchone()
        if tax_id:
            tax_id = tax_id[0]
            taxquery = "select name from taxonomy where id = \"" + str(tax_id) + "\""
            cursor.execute(taxquery)
            taxonomy = cursor.fetchone()[0]  # Returns tuple with 1 item without [0]
            stop = False
            while not stop:
                taxquery = "select TAXONOMY_id from taxonomy where id = \"" + str(tax_id) + "\""
                cursor.execute(taxquery)
                tax_id = cursor.fetchone()[0]
                taxquery = "select name from taxonomy where id = \"" + str(tax_id) + "\""
                cursor.execute(taxquery)
                tax_next = cursor.fetchone()
                if tax_next:
                    tax_next = tax_next[0]
                else:
                    return taxonomy
                taxonomy = str(tax_next) + " - " + taxonomy
                if not tax_id:
                    stop = True
            return taxonomy
        else:
            return "Taxonomy not found"

    if filename == "bacterie.html":
        # """ Als er op zoeken op bacterie naam wordt gebruikt dan wordt de bacterie.html pagina aangeroepen.
        # deze pagina moet nog aangevuld worden met de data die je kruigt als je filterd op het zoekword
        # """
        accessie = ""
        searchword = ""
        zoekwoord = ""
        teruggeven = ""
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
            try:
                accessie = request.form["accessie"]
            except KeyError:
                accessie = ""
            if zoekwoord != "":
                # als er gezocht wordt op naam dan is zoekword niet leeg dus dan wordt het volgende gedaan
                # Query die zoekt op het zoekwoord
                sql = "select blast.name, blast.accessioncode, functionality.function from " \
                      "blast left join functionint on blast.id = functionint.BLAST_id " \
                      "left join functionality on functionint.functionality_id = functionality.id " \
                      "where blast.name like '%" + zoekwoord + "%'"
                cursor.execute(sql)

                records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
                # maak een tabel in teruggeven zodat er echt iets wordt teruggeven
                teruggeven = ("<p2>Gevonden data van het zoeken op naam:</p2><br>\n"
                              + "   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                              + "   <tr>\n"
                              + "   <th onclick=\"sortTable(0)\">Naam</th>\n"
                              + "   <th onclick=\"sortTable(1)\">Accessiecode:</th>\n"
                              + "   <th onclick=\"sortTable(2)\">Functie:</th>\n"
                              + "   </tr>")
                for row in records:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td><p2>" + str(row[0]) + "</p2></td>"
                    # Maak van al de accessiecodes en een link naar de ncbi pagina
                    teruggeven = teruggeven + "<td>" \
                                              "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(row[1]) + "\">"\
                                              "" + str(row[1]) + "</a></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(row[2]) + "</p2></td>"
                    teruggeven = teruggeven + "</tr>"
                teruggeven = teruggeven + "</table>"
        if searchword != "":
            # als er gezocht wordt op naam dan is zoekword niet leeg dus dan wordt het volgende gedaan
            sql = "select blast.accessioncode, blast.name, taxonomy.name from taxonomy join blast on " \
                  "blast.TAXONOMY_id = taxonomy.id where taxonomy.name like'%" + searchword + "%'"
            cursor.execute(sql)
            data = cursor.fetchall()
            # maakt een tabel van de gevonden data
            teruggeven = ("<p2>Gevonden data van het zoeken op taxonomy:</p2><br>\n"
                          + "<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "   <tr>\n"
                          + "   <th onclick=\"sortTable(0)\">Accessiecode</th>\n"
                          + "   <th onclick=\"sortTable(1)\">Naam</th>\n"
                          + "   <th onclick=\"sortTable(2)\">Taxonomy</th>\n"
                          + "   </tr>")

            alreadyhave = []
            for a in data:
                if str(a[0]) in alreadyhave:  # For some reason "not in" seems to be significantly slower?
                    pass
                else:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td>" \
                                              "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(a[0]) + "\">" \
                                              "" + str(a[0]) + "</a></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(a[1]) + "</p2></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(taxonomies(a[2])) + "</p2></td>"
                    teruggeven = teruggeven + "</tr>"
            cursor.close()
            conn.close()

            teruggeven = teruggeven + "</table>"
        if accessie != "":
            sql = "select blast.accessioncode, blast.name from blast where blast.accessioncode like'%" + accessie + "%'"
            cursor.execute(sql)
            data = cursor.fetchall()
            # maakt een tabel van de gevonden data
            teruggeven = ("<p2>Gevonden data van het zoeken op accessiecode:</p2><br>\n"
                          + "   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "   <tr>\n"
                          + "   <th onclick=\"sortTable(0)\">Accessiecode</th>\n"
                          + "   <th onclick=\"sortTable(1)\">Naam</th>\n"
                          + "   </tr>")

            for a in data:
                teruggeven = teruggeven + "<tr>"
                teruggeven = teruggeven + "<td>" \
                                          "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(a[0]) + "\">" \
                                          "" + str(a[0]) + "</a></td>"
                teruggeven = teruggeven + "<td><p2>" + str(a[1]) + "</p2></td>"
                teruggeven = teruggeven + "</tr>"
            cursor.close()
            conn.close()

            teruggeven = teruggeven + "</table>"

        return render_template("bacterie.html", teruggeven=teruggeven, zoekwoord=zoekwoord, accessie=accessie,
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
        accessie = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                           user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                           password="ConnectionPWD")
            cursor = conn.cursor()
            naam = request.form["naam"]
            coverage = request.form["coverage"]
            score = request.form["score"]
            identity = request.form["identity"]
            # evalue = request.form["evalue"]
            accessie = request.form["accessie"]
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
            # if evalue != "":
            #     #
            #     sql = sql + " and evalue < " + evalue + "%'"
            # #
            if accessie != "":
                sql = sql + " and accessioncode like '%" + accessie + "%'"
            query = "select blast.name, evalue, bits, querycoverage, percidentity, accessioncode from blast where 1=1" \
                    + sql
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
                          + "    <th onclick=\"sortTable(5)\">Accessiecode:</th>\n"
                          + "    </tr>")
            for row in records:
                teruggeven = teruggeven + "<tr>"
                teruggeven = teruggeven + "<td><p2>" + str(row[0]) + "</p2></td>"
                teruggeven = teruggeven + "<td><p2>" + str(row[1]) + "</p2></td>"
                teruggeven = teruggeven + "<td><p2>" + str(row[2]) + "</p2></td>"
                teruggeven = teruggeven + "<td><p2>" + str(row[3]) + "</p2></td>"
                teruggeven = teruggeven + "<td><p2>" + str(row[4]) + "</p2></td>"
                teruggeven = teruggeven + "<td>" \
                                          "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(row[5]) + "\">"\
                                          "" + str(row[5]) + "</a></td>"
                teruggeven = teruggeven + "</tr>"
            teruggeven = teruggeven + "</table>"
        return (render_template("tabel.html", teruggeven=teruggeven, naam=naam, identity=identity, score=score,
                                evalue=evalue, coverage=coverage, accessie=accessie))
        # except:
        #     teruggeven = "Verkeerde zoek opdracht ingegeven. " + "<br>" + \
        #                  "Vul alleen bij de naam een woord in en bij de rest alleen getallen."
        #     return render_template("tabel.html", teruggeven=teruggeven)

    elif filename == "seqs.html":
        # """ Als er op zoeken op bacterie naam wordt gebruikt dan wordt de bacterie.html pagina aangeroepen.
        # deze pagina moet nog aangevuld worden met de data die je kruigt als je filterd op het zoekword
        # """
        accessie = ""
        searchword = ""
        zoekwoord = ""
        teruggeven = ""
        conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                       user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                       password="ConnectionPWD")
        cursor = conn.cursor()
        if request.method == 'POST':
            try:
                zoekwoord = request.form["zoekwoord"]
            except KeyError:
                zoekwoord = ""
            try:
                searchword = request.form["searchword"]
            except KeyError:
                searchword = ""
            try:
                accessie = request.form["accessie"]
            except KeyError:
                accessie = ""
            if zoekwoord != "":
                # Query die zoekt op het zoekwoord
                sql = "select blast.name, blast.accessioncode, sequence from " \
                      "blast join sequence on blast.SEQUENCE_id = sequence.id " \
                      "where blast.name like '%" + zoekwoord + "%'"
                cursor.execute(sql)

                records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
                teruggeven = ("<p2>Gevonden data van het zoeken op naam:</p2><br>\n"
                              + "<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                              + "   <tr>\n"
                              + "   <th onclick=\"sortTable(0)\">Naam</th>\n"
                              + "   <th onclick=\"sortTable(1)\">Accessiecode:</th>\n"
                              + "   <th onclick=\"sortTable(2)\">Sequentie:</th>\n"
                              + "   </tr>")
                for row in records:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td><p2>" + str(row[0]) + "</p2></td>"
                    teruggeven = teruggeven + "<td>" \
                                              "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(row[1]) + "\">"\
                                              "" + str(row[1]) + "</a></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(row[2]) + "</p2></td>"
                    teruggeven = teruggeven + "</tr>"
                teruggeven = teruggeven + "</table>"
        if searchword != "":
            print("hoi")
            sql = "select blast.accessioncode, blast.name, taxonomy.name, sequence from taxonomy join blast on " \
                  "blast.TAXONOMY_id = taxonomy.id join sequence on blast.SEQUENCE_id = sequence.id " \
                  " where taxonomy.name like'%" + searchword + "%'"
            cursor.execute(sql)
            data = cursor.fetchall()

            # maakt een tabel van de gevonden data
            teruggeven = ("<p2>Gevonden data van het zoeken op taxonomy:</p2><br>\n"
                          + "<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "   <tr>\n"
                          + "   <th onclick=\"sortTable(0)\">Accessiecode</th>\n"
                          + "   <th onclick=\"sortTable(1)\">Naam</th>\n"
                          + "   <th onclick=\"sortTable(2)\">Taxonomy</th>\n"
                          + "   <th onclick=\"sortTable(3)\">Sequenties</th>\n"
                          + "   </tr>")

            alreadyhave = []
            print(data)
            for a in data:
                print(a)
                if str(a[0]) in alreadyhave:  # For some reason "not in" seems to be significantly slower?
                    pass
                else:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td>" \
                                              "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(a[0]) + "\">" \
                                              "" + str(a[0]) + "</a></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(a[1]) + "</p2></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(taxonomies(a[2])) + "</p2></td>"
                    teruggeven = teruggeven + "<td><p2>" + str(a[3]) + "</p2></tb>"
                    teruggeven = teruggeven + "</tr>"
            cursor.close()
            conn.close()
            teruggeven = teruggeven + "</table>"
        if accessie != "":
            sql = "select blast.accessioncode, blast.name, sequence from blast join sequence on blast.SEQUENCE_" \
                  "id = sequence.id where blast.accessioncode like'%" + accessie + "%'"
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            # maakt een tabel van de gevonden data
            teruggeven = ("<p2>Gevonden data van het zoeken op accessiecode:</p2><br>\n"
                          + "   <table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "   <tr>\n"
                          + "   <th onclick=\"sortTable(0)\">Accessiecode</th>\n"
                          + "   <th onclick=\"sortTable(1)\">Naam</th>\n"
                          + "   <th onclick=\"sortTable(2)\">Sequenties</th>\n"
                          + "   </tr>")

            for a in data:
                teruggeven = teruggeven + "<tr>"
                teruggeven = teruggeven + "<td>"\
                                          "<a href = \"https://www.ncbi.nlm.nih.gov/protein/" + str(a[0]) + "\">" \
                                          "" + str(a[0]) + "</a></td>"
                teruggeven = teruggeven + "<td><p2>" + str(a[1]) + "<p2></td>"
                teruggeven = teruggeven + "<td><p2>" + str(a[2]) + "<p2></td>"
                teruggeven = teruggeven + "</tr>"

            teruggeven = teruggeven + "</table>"

        return render_template("seqs.html", teruggeven=teruggeven, zoekwoord=zoekwoord, accessie=accessie,
                               searchword=searchword)

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
            conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                           user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                           password="ConnectionPWD")
            cursor = conn.cursor()
            cursor.execute("select name, count(*) from blast group by name order by 2 desc")
            gegevens = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
            cursor.close()
            conn.close()
            giveback = "['Naam', '%'],"
            #
            for row in gegevens:
                giveback = giveback + "['" + str(row[0]) + "', " + str(row[1]) + " ],"
            giveback = giveback[:-1]
            return render_template("statistiek.html", teruggeven=teruggeven, giveback = giveback)
        # except:
        #     return render_template("error.html")

    elif filename == "zelfblast.html":
        seq = ""
        teruggeven = ""
        if request.method == 'POST':
            try:
                seq = request.form["iets"]
            except:
                seq = "Geef sequentie in"
            print(seq)
            if seq is not None:
                result_handle = NCBIWWW.qblast("blastx", "nr", seq)
                blast_records = NCBIXML.parse(result_handle)
                blast_record = next(blast_records)
                teruggeven = "<br>"
                print("blasten")
                print(blast_records)
                for alignment in blast_record.alignments:
                    print("alignment")
                    for hsp in alignment.hsps:
                        print("hsp")
                        teruggeven = str(teruggeven) + str('---------------------------------') + "<br>"
                        teruggeven = teruggeven + 'sequence: ' + str(alignment.title) + "<br>"
                        teruggeven = teruggeven + 'lengte: ' + str(alignment.length) + "<br>"
                        teruggeven = teruggeven + 'e-value' + str(hsp.expect) + "<br>"
                        teruggeven = teruggeven + str(hsp.query) + "<br>"
                        teruggeven = teruggeven + str(hsp.match) + "<br>"
                        teruggeven = teruggeven + str(hsp.sbjct) + "<br>"
                print("geblast")
                if teruggeven == "<br>":
                    teruggeven = teruggeven + "Geen blast resultaten"
                print(teruggeven)
        return render_template("zelfblast.html", teruggeven=teruggeven, seq=seq)
    else:
        resp = make_response(render_template(filename))
        return resp


if __name__ == '__main__':
    app.run()
