import logging.handlers
import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from charset_normalizer import from_path
from werkzeug.utils import secure_filename
from ffcuesplitter.cuesplitter import InvalidFileError
from ffcuesplitter.cuesplitter import FFCueSplitterError
from werkzeug.middleware.proxy_fix import ProxyFix
import logging
import splitter

#flask --app api run --host='0.0.0.0'

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'flac', 'ape', 'mp3', 'wav', 'ogg'}
ALLOWED_CUE = {'cue'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.wsgi_app = ProxyFix(
#    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
#)
app.secret_key = os.urandom(24)

el_logger = logging.getLogger()
consoleHandler = logging.StreamHandler()
el_logger.addHandler(consoleHandler)
fileHandler = logging.handlers.RotatingFileHandler("logs.log", backupCount=100, maxBytes=1048576, encoding='utf-8')
el_logger.addHandler(fileHandler)

def allowed_audio(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_cue(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_CUE

def mod_cue_target_file(cue_sheet):
    cue_path=os.path.join(app.config['UPLOAD_FOLDER'], cue_sheet)
    expected_audio_file = None

    if os.path.exists(cue_path): # Si el cue está en el servidor
        result = from_path(cue_path)
        best_match = result.best()
        #cue_en_lista = best_match.decoded.splitlines(keepends=True)
        with open(cue_path, 'r', encoding=best_match.encoding) as mod_cue:
            cue_en_lista = [line for line in mod_cue]
        print("--------------------------------------")
        for i in range(len(cue_en_lista)):
            if cue_en_lista[i].split(' ')[0] == "FILE":
                el_split = cue_en_lista[i].split('\"')
                el_split[1] = secure_filename(el_split[1])
                expected_audio_file = el_split[1]
                cue_en_lista[i] = '\"'.join(el_split)
        with open(cue_path, 'w', encoding=best_match.encoding) as mod_cue:
            mod_cue.writelines(cue_en_lista)
        print(f"CUE adjusted | Text codec: {best_match.encoding}")      
        print("--------------------------------------")

    return expected_audio_file

def process_files(cue_file, audio_file):
    cue_name = secure_filename(cue_file.filename)
    cue_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cue_name))
    expected_audio_file=mod_cue_target_file(cue_name)
    if audio_file.filename == '' or not audio_file:
        return redirect(request.url)
    if audio_file and allowed_audio(audio_file.filename):
        audio_name = secure_filename(audio_file.filename)
        if(expected_audio_file != audio_name):
            flash("The name of the audio file provided and the name of the audio file expected are different.")
            filenames = []
            filenames.append(cue_file)
            filenames.append(audio_file)
            return render_template("error_template.html", files=filenames)
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_name))
        return redirect(url_for('info_cue', name=cue_name))
    else:
        flash("not a valid audio file")
        filenames = []
        filenames.append(cue_file)
        filenames.append(audio_file)
        return render_template("error_template.html", files=filenames)

@app.route('/upload', methods=['GET'])
def wellcome():
    return render_template('upload.html')


@app.route("/upload", methods=["POST"])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file_cue' not in request.files or 'file_audio' not in request.files:
            return redirect(request.url)
        
        cue_file = request.files['file_cue']
        audio_file = request.files['file_audio']
        print(cue_file)
        print(audio_file)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if cue_file.filename == '' or not cue_file:
            return redirect(request.url)
        
        if allowed_cue(cue_file.filename):
            return process_files(cue_file, audio_file)
            
        elif allowed_cue(audio_file.filename):
            cue_file = request.files['file_audio']
            audio_file = request.files['file_cue']

            return process_files(cue_file, audio_file)
            
        else:
            flash("The .cue file is missing")
            filenames = []
            filenames.append(cue_file)
            filenames.append(audio_file)
            return render_template("error_template.html", files=filenames)

@app.route('/info/<name>', methods=['GET'])
def info_cue(name):
    try:
        respuesta = splitter.album_info(os.path.join(app.config['UPLOAD_FOLDER'], name))
        respuesta['cue_file'] = name
        return render_template('info.html', respuesta=respuesta)
    except InvalidFileError:
        error = {}
        error['error'] = "InvalidFileError: "+name+" no existe en el directorio."
        return error
    except FFCueSplitterError:
        error = {}
        error['error'] = "FFCueSplitterError: el archivo de audio no existe o no se puede abrir."
        return error

@app.route('/info/<name>', methods=['POST'])
def download_file(name):
    try:
        comprimido = splitter.split_it_like_solomon(
            cue_file=os.path.join(app.config['UPLOAD_FOLDER'], name),
            output_format=request.form.get("output_format"),
            flac_compression_level=request.form.get("flac_compression_level"),
            flac_ar=request.form.get("flac_ar"),
            flac_sample_fmt=request.form.get("flac_sample_fmt"),
            wav_pcm=request.form.get("flac_sample_fmt"),
            wav_ar=request.form.get("wav_ar"),
            ogg_bitrate=request.form.get("ogg_bitrate"),
            ogg_quality=request.form.get("ogg_quality"),
            ogg_ar=request.form.get("mp3_bitrate"),
            mp3_bitrate=request.form.get("mp3_bitrate"),
            mp3_ar=request.form.get("mp3_ar")
        )
        respuesta = send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[2])
        respuesta.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return respuesta
        #return send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[2], as_attachment=True)
    except InvalidFileError:
        error = {}
        error['error'] = "InvalidFileError: "+name+" no existe en el directorio."
        return error
    except FFCueSplitterError:
        error = {}
        error['error'] = "FFCueSplitterError: el archivo de audio no existe o no se puede abrir."
        return error

#@app.route('/info/<name>', methods=['POST'])
#def fake_download(name):
#    print("output_format: "+request.form.get("output_format"))
#    print("flac_compression_level: "+request.form.get("flac_compression_level"))
#    print("flac_ar: "+request.form.get("flac_ar"))
#    print("flac_sample_fmt: "+request.form.get("flac_sample_fmt"))
#    print("wav_pcm: "+request.form.get("wav_pcm"))
#    print("wav_ar: "+request.form.get("wav_ar"))
#    print("ogg_codec: "+request.form.get("ogg_codec"))
#    print("ogg_quality: "+request.form.get("ogg_quality"))
#    print("ogg_ar: "+request.form.get("ogg_ar"))
#    print("mp3_bitrate: "+request.form.get("mp3_bitrate"))
#    print("mp3_ar: "+request.form.get("mp3_ar"))
#    return f"""
#    <!DOCTYPE html>
#    <title>Upload the files</title>
#    <h1>Hora de mirar lo que se subio</h1>
#    <h2><a href="/info/{name}">Volver a probar</a></h2>
#    </html>
#    """


#@app.route("/upload", methods=["POST"])
#def upload():
#    #uploaded_files = request.files.getlist("file[]")
#    #print(uploaded_files)
#    cue = request.files['file_cue']
#    audio = request.files['file_audio']
#    print(cue)
#    print(audio)
#    #flash('holy shit im flashing')
#    return "Look what happend"

############################################
# This is a version of the upload function #
# for the case in which the submit form    #
# appends the files in a list instead of   #
# two different variables.                 #
############################################

#@app.route("/upload", methods=["POST"])
#def upload():
#    if request.method == 'POST':
#        # check if the post request has the file part
#        if 'file[]' not in request.files:
#            return redirect(request.url)
#        
#        uploaded_files = request.files.getlist("file[]")
#        if len(uploaded_files) != 2:
#            flash("2 files are needed, neither more nor less")
#            filenames = []
#            for i in range(len(uploaded_files)):
#                filenames.append(uploaded_files[i].filename)
#            return render_template("error_template.html", files=filenames)
#        
#        cue_file = uploaded_files[0]
#        audio_file = uploaded_files[1]
#
#        # If the user does not select a file, the browser submits an
#        # empty file without a filename.
#        if cue_file.filename == ''or not cue_file:
#            return redirect(request.url)
#        
#        if allowed_cue(cue_file.filename):
#            cue_name = secure_filename(cue_file.filename)
#            cue_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cue_name))
#            mod_cue_target_file(cue_name)
#            if audio_file.filename == '':
#                return redirect(request.url)
#            if audio_file and allowed_audio(audio_file.filename):
#                audio_name = secure_filename(audio_file.filename)
#                audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_name))
#                return redirect(url_for('info_cue', name=cue_name))
#            else:
#                flash("not a valid audio file")
#                filenames = []
#                for i in range(len(uploaded_files)):
#                    filenames.append(uploaded_files[i].filename)
#                return render_template("error_template.html", files=filenames)
#            
#        elif allowed_cue(audio_file.filename):
#            cue_file = uploaded_files[1]
#            audio_file = uploaded_files[0]
#
#            cue_name = secure_filename(cue_file.filename)
#            cue_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cue_name))
#            mod_cue_target_file(cue_name)
#            if audio_file.filename == '' or not audio_file:
#                return redirect(request.url)
#            if audio_file and allowed_audio(audio_file.filename):
#                audio_name = secure_filename(audio_file.filename)
#                audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_name))
#                return redirect(url_for('info_cue', name=cue_name))
#            else:
#                flash("not a valid audio file")
#                filenames = []
#                for i in range(len(uploaded_files)):
#                    filenames.append(uploaded_files[i].filename)
#                return render_template("error_template.html", files=filenames)
#            
#        else:
#            flash("The .cue file is missing")
#            filenames = []
#            for i in range(len(uploaded_files)):
#                filenames.append(uploaded_files[i].filename)
#            return render_template("error_template.html", files=filenames)