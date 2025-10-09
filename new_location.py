from flask import Flask, render_template_string, request, redirect, url_for
from github import Github
import base64
import csv
import io

app = Flask(__name__)

# GitHub setup
GITHUB_TOKEN = "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"
REPO_NAME = "nollet-ewout/zijn-we-weg-"
CSV_PATH = "reislocatie_filter.csv"

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# HTML template met één vraag per pagina (bijvoorbeeld locatie naam)
form_template = """
<!doctype html>
<title>Nieuwe locatie toevoegen</title>
<h2>Voer gegevens locatie in</h2>
<form method=post>
  <label>Naam locatie:</label>
  <input type=text name=naam required>
  <br><br>
  <label>Adres:</label>
  <input type=text name=adres required>
  <br><br>
  <label>Beschrijving:</label>
  <input type=text name=beschrijving required>
  <br><br>
  <input type=submit value=Opslaan>
</form>
"""

@app.route("/nieuw", methods=["GET", "POST"])
def nieuw():
    if request.method == "POST":
        naam = request.form['naam']
        adres = request.form['adres']
        beschrijving = request.form['beschrijving']

        # Lees huidige CSV uit GitHub
        contents = repo.get_contents(CSV_PATH)
        csv_data = base64.b64decode(contents.content).decode('utf-8')

        # Voeg nieuwe rij toe
        f = io.StringIO(csv_data)
        reader = list(csv.reader(f))
        reader.append([naam, adres, beschrijving])

        # Schrijf terug naar CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(reader)
        updated_csv = output.getvalue()

        # Update bestand op GitHub
        repo.update_file(
            path=CSV_PATH,
            message=f"Toevoegen locatie: {naam}",
            content=updated_csv,
            sha=contents.sha,
            branch="main"  # Pas aan indien nodig
        )

        return redirect(url_for('nieuw'))

    return render_template_string(form_template)


#if __name__ == "__main__":
#    app.run(debug=True)
