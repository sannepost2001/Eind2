# Sanne Post
# 18-5-19
# Website champignon compost
import mysql.connector
from flask import Flask, request, render_template, make_response, send_from_directory

app = Flask(__name__)


@app.route('/')
def home():
    resp = make_response(render_template('home.html'))
    return resp


@app.route('/<path:filename>', methods=['GET', 'POST'])

def pagina(filename):
    if filename == "bacterie.html":
        zoekwoord = ""
        teruggeven = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="ensembldb.ensembl.org", user="anonymous", db="homo_sapiens_core_95_38")
            cursor = conn.cursor()
            zoekwoord = request.form["zoekwoord"]
            cursor.execute("select description from gene where description like '%" + zoekwoord + "%'")
            records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
            cursor.close()
            conn.close()
            teruggeven = ""
            for row in records:
                teruggeven = teruggeven + (row[0])
                teruggeven = teruggeven + "<br>"
        return (render_template("bacterie.html", teruggeven=teruggeven, zoekwoord=zoekwoord))
    elif filename == "tabel.html":
        teruggeven = ""
        sql = ""
        naam = ""
        coverage = ""
        score = ""
        identity = ""
        evalue = ""
        if request.method == 'POST':
            conn = mysql.connector.connect(host="ensembldb.ensembl.org", user="anonymous", db="homo_sapiens_core_95_38")
            cursor = conn.cursor()
            naam = request.form["naam"]
            coverage = request.form["coverage"]
            score = request.form["score"]
            identity = request.form["identity"]
            evalue = request.form["evalue"]
            if naam != "":
                sql = sql + " and description like '%" + naam + "%'"
            if coverage != "":
                sql = sql + " and description like '%" + coverage + "%'"
            if score != "":
                sql = sql + " and description like '%" + score + "%'"
            if identity != "":
                sql = sql + " and description like '%" + identity + "%'"
            if evalue != "":
                sql = sql + " and description like '%" + evalue + "%'"
            cursor.execute("select description from gene where 1=1 " + sql)
            records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
            cursor.close()
            conn.close()
            teruggeven = ("<table id=\"myTable\" style=\"width:777px; height: 400px;\">"
                          + "<tr>\n"
                          + "    <th onclick=\"sortTable(0)\">Naam</th>\n"
                          + "    <th onclick=\"sortTable(1)\">E-value:</th>\n"
                          + "    <th onclick=\"sortTable(2)\">Bit)score:</th>\n"
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
        conn = mysql.connector.connect(host="ensembldb.ensembl.org", user="anonymous", db="homo_sapiens_core_95_38")
        cursor = conn.cursor()
        cursor.execute("select description, count(*) from gene group by description order by 2 desc limit 5")
        records = cursor.fetchall()  # lijst met al de namen die het zoekwoord in de naam hebben
        cursor.close()
        conn.close()
        teruggeven = "['Naam', '%'],"
        for row in records:
            teruggeven = teruggeven + "['" + str(row[0]) + "', " + str(row[1]) + " ],"
        teruggeven = teruggeven[:-1]
        return (render_template("statistiek.html", teruggeven=teruggeven))
    else:
        resp = make_response(render_template(filename))
        return resp


if __name__ == '__main__':
    app.run()
