# Sanne Post
# 18-5-19
# Website champignon compost
import mysql.connector
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
    if filename == "bacterie.html":
        # """ Als er op zoeken op bacterie naam wordt gebruikt dan wordt de bacterie.html pagina aangeroepen.
        # deze pagina moet nog aangevuld worden met de data die je kruigt als je filterd op het zoekword
        # """

        zoekwoord = ""
        teruggeven = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                           user="kxxxf@hannl-hlo-bioinformatica-mysqlsrv", db="kxxxf",
                                           password="ConnectionPWD")
            cursor = conn.cursor()
            zoekwoord = request.form["zoekwoord"]
            # Query die zoekt op het zoekwoord
            cursor.execute("""select blast.name, blast.accessioncode, functionality.function from blast join functionint
                              on blast.id = functionint.BLAST_id join functionality on functionint.functionality_id = 
                              functionality.id where blast.name like '%" + zoekwoord + "%'""")
            records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
            cursor.close()
            conn.close()
            # maakt een tabel van de gevonden data
            teruggeven = ("<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "   <tr>\n"
                          + "   <th onclick=\"sortTable(0)\">Naam</th>\n"
                          + "   <th onclick=\"sortTable(1)\">Accessiecode:</th>\n"
                          + "   <th onclick=\"sortTable(2)\">Functie:</th>\n"
                          + "   </tr>")
            for rows in records:
                for row in rows:
                    teruggeven = teruggeven + "<tr>"
                    teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                    teruggeven = teruggeven + "<td>" + (row[1]) + "</td>"
                    teruggeven = teruggeven + "<td>" + (row[2]) + "</td>"
                    teruggeven = teruggeven + "</tr>"
            teruggeven = teruggeven + "</table>"
        return render_template("bacterie.html", teruggeven=teruggeven, zoekwoord=zoekwoord)

    elif filename == "tabel.html":
        """"""
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
                sql = sql + " and sequence.score > " + score
            if identity != "":
                #
                sql = sql + " and percidentity > " + identity
            if evalue != "":
                #
                sql = sql + " and evalue < " + evalue + "%'"
            #
            cursor.execute("""select blast.name, evalue, sequence.score, querycoverage, percidentity from blast join 
                           sequence on blast.id = sequence.id where 1=1 """ + sql)
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
                teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                teruggeven = teruggeven + "<td>" + (row[0]) + "</td>"
                teruggeven = teruggeven + "</tr>"
            teruggeven = teruggeven + "</table>"
        return (render_template("tabel.html", teruggeven=teruggeven, naam=naam, identity=identity, score=score,
                                evalue=evalue, coverage=coverage))
    elif filename == "statistiek.html":
        """"""
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
        return (render_template("statistiek.html", teruggeven=teruggeven))
    else:
        #
        resp = make_response(render_template(filename))
        return resp


if __name__ == '__main__':
    app.run()
