from flask import Flask, render_template, request, redirect, url_for, send_file
import csv
import os

app = Flask(__name__)
CSV_FILE = 'words.csv'

def init_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['word', 'meaning', 'status', 'created_at'])

def read_words():
    words = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            words.append(row)
    return words

def add_word(word, meaning):
    from datetime import datetime
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([word, meaning, '未学习', datetime.now().strftime('%Y-%m-%d')])

def delete_word(word):
    words = read_words()
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'meaning', 'status', 'created_at'])
        for w in words:
            if w['word'] != word:
                writer.writerow([w['word'], w['meaning'], w['status'], w['created_at']])

def update_status(word, status):
    words = read_words()
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['word', 'meaning', 'status', 'created_at'])
        for w in words:
            if w['word'] == word:
                writer.writerow([w['word'], w['meaning'], status, w['created_at']])
            else:
                writer.writerow([w['word'], w['meaning'], w['status'], w['created_at']])

@app.route('/')
def index():
    search = request.args.get('search', '')
    words = read_words()
    if search:
        words = [w for w in words if search.lower() in w['word'].lower() or search in w['meaning']]
    return render_template('index.html', words=words, search=search)

@app.route('/add', methods=['POST'])
def add():
    word = request.form.get('word', '').strip()
    meaning = request.form.get('meaning', '').strip()
    if word and meaning:
        add_word(word, meaning)
    return redirect(url_for('index'))

@app.route('/delete/<word>')
def delete(word):
    delete_word(word)
    return redirect(url_for('index'))

@app.route('/toggle/<word>')
def toggle(word):
    words = read_words()
    for w in words:
        if w['word'] == word:
            new_status = '已学习' if w['status'] == '未学习' else '未学习'
            update_status(word, new_status)
            break
    return redirect(url_for('index'))

@app.route('/export')
def export():
    return send_file(CSV_FILE, as_attachment=True, download_name='words.csv')

@app.route('/import', methods=['POST'])
def import_words():
    file = request.files.get('file')
    if file:
        reader = csv.reader(file.read().decode('utf-8').splitlines())
        next(reader, None)
        for row in reader:
            if len(row) >= 2:
                add_word(row[0], row[1])
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_csv()
    app.run(debug=True, port=5000)