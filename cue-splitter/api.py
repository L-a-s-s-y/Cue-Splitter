import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template, flash
from charset_normalizer import from_path
from werkzeug.utils import secure_filename
from ffcuesplitter.cuesplitter import InvalidFileError
from ffcuesplitter.cuesplitter import FFCueSplitterError
from werkzeug.middleware.proxy_fix import ProxyFix
from pathlib import Path
import logging
import splitter

#flask --app api run --host='0.0.0.0'

UPLOAD_FOLDER = '/tmp/splitter'
ALLOWED_EXTENSIONS = {'flac', 'ape', 'mp3', 'wav', 'ogg', 'wv'}
ALLOWED_CODECS = {'flac', 'opus', 'mp3', 'wav', 'ogg'}
ALLOWED_CUE = {'cue'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)
# Needed in order to use the flash method in flask
app.secret_key = os.urandom(24)

def allowed_audio(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#def allowed_codec(filename):
#    return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_CODECS

def allowed_cue(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_CUE

def check_codec_target_file(cue_sheet):
    cue_path = os.path.join(app.config['UPLOAD_FOLDER'], cue_sheet)
    codec_allowed = False

    if os.path.exists(cue_path): # Si el cue está en el servidor
        result = from_path(cue_path)
        best_match = result.best()
        with open(cue_path, 'r', encoding=best_match.encoding) as mod_cue:
            cue_en_lista = [line for line in mod_cue]
        for i in range(len(cue_en_lista)):
            if cue_en_lista[i].split(' ')[0] == "FILE":
                audio_file = cue_en_lista[i].split('\"')
                codec_allowed = check_codec_target_file(audio_file[1])
    return codec_allowed

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
            filenames.append(expected_audio_file)
            filenames.append(audio_name)
            return render_template("error_template.html", files=filenames)
        audio_file.save(os.path.join(app.config['UPLOAD_FOLDER'], audio_name))
        return redirect(url_for('info_cue', name=cue_name))
    else:
        flash("not a valid audio file")
        filenames = []
        filenames.append(cue_file)
        filenames.append(audio_file)
        return render_template("error_template.html", files=filenames)

@app.route('/')
def root():
    return redirect(url_for('wellcome'))

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
        return render_template('info.jinja', respuesta=respuesta)
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
            wv_compression_level=request.form.get("wv_compression_level"),
            wv_ar=request.form.get("wv_ar"),
            wv_sample_fmt=request.form.get("wv_sample_fmt"),
            wv_bitrate=request.form.get("wv_bitrate"),
            wav_pcm=request.form.get("wav_pcm"),
            wav_ar=request.form.get("wav_ar"),
            ogg_bitrate=request.form.get("ogg_bitrate"),
            ogg_quality=request.form.get("ogg_quality"),
            ogg_ar=request.form.get("ogg_ar"),
            mp3_bitrate=request.form.get("mp3_bitrate"),
            mp3_ar=request.form.get("mp3_ar"),
            orig_codec=request.form.get("orig_codec"),
            orig_sample_rate=request.form.get("orig_sample_rate"),
            orig_sample_fmt=request.form.get("orig_sample_fmt")
        )

        zip_path = Path(comprimido).resolve()
        zip_name = str(zip_path.stem)+'.zip'
        respuesta = send_from_directory(app.config['UPLOAD_FOLDER'], zip_name)
        #respuesta = send_from_directory(app.config['UPLOAD_FOLDER'], comprimido.split('/')[-1])
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