import mysql.connector
# from flask import request

host = "hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com"
user = "kxxxf@hannl-hlo-bioinformatica-mysqlsrv"
passw = "ConnectionPWD"
dbname = "kxxxf"
database = mysql.connector.connect(host=host, user=user, password=passw, db=dbname)
cursor = database.cursor()


# @app.route('/taxonomy)')
def taxonomies(nameinput):
    # nameinput = request.args.get("nameinput")
    cursor.execute("select id from taxonomy where name = \""+nameinput+"\" limit 1")
    tax_id = cursor.fetchone()
    if tax_id:
        tax_id = tax_id[0]
        query = "select name from taxonomy where id = \""+str(tax_id)+"\""
        cursor.execute(query)
        taxonomy = cursor.fetchone()[0]  # Returns tuple with 1 item without [0]
        stop = False
        while not stop:
            query = "select TAXONOMY_id from taxonomy where id = \""+str(tax_id)+"\""
            cursor.execute(query)
            tax_id = cursor.fetchone()[0]
            query = "select name from taxonomy where id = \""+str(tax_id)+"\""
            cursor.execute(query)
            tax_next = cursor.fetchone()
            if tax_next:
                tax_next = tax_next[0]
            else:
                return taxonomy
            taxonomy = str(tax_next)+" - "+taxonomy
            if not tax_id:
                stop = True
        return taxonomy
    else:
        return False  # Or None or an error string or something


# name_input = input("Get taxonomy of?")
name_input = "Bacillus akibai"
print(taxonomies(name_input))

cursor.close()
database.close()

"""
Input : Name (Bijv. "Bacillus akibai", dan terug gaan tot Null (cellular organisms))
Output: Volgorde taxonomie (Bijv. Taxonomy_ID 1 bij Taxonomy_ID)
        String Groot(lage ID)-Klein(Hoge ID)

"""