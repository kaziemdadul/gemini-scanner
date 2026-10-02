import os
import subprocess
import sys
from flask import Flask, render_template, Response, send_file, abort

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run')
def run_script():
    def generate():
        # Using sys.executable to ensure we use the same Python interpreter
        env = dict(os.environ)
        env['PYTHONIOENCODING'] = 'utf-8'
        process = subprocess.Popen(
            [sys.executable, '-u', 'gemini18msc.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            bufsize=1,
            env=env
        )
        for line in iter(process.stdout.readline, ''):
            yield f"data: {line}\n\n"
        process.stdout.close()
        process.wait()
        yield f"data: [PROCESS_COMPLETED]\n\n"
        
    return Response(generate(), mimetype='text/event-stream')

@app.route('/download/<filename>')
def download_file(filename):
    if filename in ['gemini_activation_links.txt', 'gemini_results.csv']:
        if os.path.exists(filename):
            return send_file(filename, as_attachment=True)
        else:
            abort(404, description="File not found. Run a scan first.")
    abort(403, description="Unauthorized")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
