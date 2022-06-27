import math

from flask import Blueprint, render_template, send_file, request, jsonify
from flask_login import current_user
from extentions import permission_required, db, aws_client
from backlog.forms import FileForm
from datetime import datetime
from werkzeug.utils import secure_filename
from backlog.models import BacklogProbe
from users.models import Users
import os.path
import pandas as pd

backlog = Blueprint('backlog', __name__, url_prefix='/backlog', template_folder='templates', static_folder='static')

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'backlog', 'uploads')
DOWNLOAD_FOLDER = os.path.join('backlog', 'downloads')
DOWNLOAD_TEMP_FOLDER = os.path.join('backlog', 'downloads', 'temp')

BUCKET = 'rdadash-jgvictors'


@backlog.route('/', methods=['GET', 'POST'])
@permission_required('backlog.view')
def thebacklog():
    form = FileForm()
    try:
        on_bucket = aws_client().list_objects_v2(Bucket=BUCKET, Prefix=DOWNLOAD_FOLDER.replace('\\', '/')).get('Contents')
        on_bucket.pop(0)
        for fb in on_bucket:
            fbn = fb.get('Key')
            if not os.path.exists(fbn):
                aws_client().download_file(BUCKET, fbn, fbn)
    except Exception as e:
        return render_template('500', e=e), 500
    dtls = []
    for f in os.listdir(DOWNLOAD_FOLDER):
        if 'Backlog NOC' in f and 'temp' not in f:
            dtls.append(datetime.fromtimestamp(float(f.split(" ")[-1].split('.')[0])))

    return render_template('backlog.html', dtls=sorted(dtls, reverse=True), form=form)


@backlog.route('/<int:time>')
@permission_required('backlog.view')
def access(time: int):
    fileloc = backlog_fileloc(float(time))
    if not os.path.exists(fileloc):
        return render_template('404.html'), 404
    try:
        df = pd.read_excel(fileloc, index_col='Ticket')
        last_probes = get_tickets_last_probes(time)
        for ticket, probe in last_probes.items():
            df['Justificativa / Ação'][int(ticket)] = probe['probe']
            df['Analista'][int(ticket)] = probe['prober_username']
        nan = df['Justificativa / Ação'].isna().sum()
    except Exception as e:
        return render_template('500.html', e=e), 500
    return render_template('backlog_access.html', df=df, nan=nan, time=time)


@backlog.route('/<int:time>/probe/<int:ticket>', methods=['POST'])
@permission_required('backlog.probe')
def probe(time: int, ticket: int):
    if 'probe' not in request.form:
        return "", 400
    probe_txt = request.form['probe']
    if not os.path.exists(backlog_fileloc(float(time))):
        return "", 404
    prb = BacklogProbe(time, ticket, probe_txt, current_user.username)
    try:
        db.session.add(prb)
        db.session.commit()
    except Exception as e:
        return render_template('500.html', e=e), 500
    return jsonify({'prober_username': prb.prober_username}), 200


def get_tickets_last_probes(time: int):
    if not os.path.exists(backlog_fileloc(float(time))):
        return "", 404
    prbs = BacklogProbe.query.filter_by(backlog_timeref=time).order_by(BacklogProbe.id.desc())
    prbs_return = {}

    for prb in prbs:
        if prb.ticket_probed in prbs_return:
            continue
        prbs_return[prb.ticket_probed] = {'id': prb.id,
                                          'probe': prb.probe,
                                          'prober_username': prb.prober_username,
                                          'date_probed': prb.date_probed}

    return prbs_return


@backlog.route('/<int:time>/get_ticket_probe/<int:ticket>',  methods=['POST'])
@permission_required('backlog.view')
def get_ticket_last_probe(time: int, ticket: int):
    prbs = BacklogProbe.query.filter_by(backlog_timeref=time, ticket_probed=ticket)
    if prbs.count() < 1:
        return '', 404
    prb = prbs.order_by(BacklogProbe.id.desc()).first()
    prb = jsonify({'id': prb.id,
                   'probe': prb.probe,
                   'prober_username': prb.prober_username,
                   'date_probed': prb.date_probed})
    return prb


@backlog.route('/download/<int:time>')
@permission_required('backlog.download')
def download(time: int):
    fileloc = backlog_fileloc(float(time))
    if not os.path.exists(fileloc):
        return render_template('404.html'), 404

    temp_fileloc = backlog_fileloc(time, True)

    try:
        df = pd.read_excel(fileloc, index_col='Ticket')
        last_probes = get_tickets_last_probes(time)
        for ticket, probe in last_probes.items():
            df['Justificativa / Ação'][int(ticket)] = probe['probe']
            df['Analista'][int(ticket)] = Users.query.get(probe['prober_username']).nome
        df.to_excel(temp_fileloc)
    except Exception as e:
        return render_template('500.html', e=e), 500

    return send_file(temp_fileloc)


@backlog.route('/upload', methods=['POST'])
@permission_required('backlog.upload')
def upload():
    file = request.files.get('file')
    if not file:
        return "", 400
    if not file.filename.endswith('.xls'):
        return "", 415

    agora = datetime.now()
    temp_save_path = os.path.join(UPLOAD_FOLDER, str(int(agora.timestamp())) + '_' + secure_filename(file.filename))

    try:
        file.save(temp_save_path)

        try:
            df = pd.read_html(temp_save_path, index_col='Ticket')
            df[0].to_excel(temp_save_path.replace('.xls', '.xlsx'))
            os.remove(temp_save_path)
            temp_save_path = temp_save_path.replace('.xls', '.xlsx')

            df = pd.read_excel(temp_save_path)

            df = df.set_index('Ticket')
            df = df[df['Área Responsável'] == 'NOC']
            df = df[df['Tempo Decorrido'] != '<=4h']
            df = df[df['Tempo Decorrido'] != '>4h']
            df = df[df['Tempo Decorrido'] != '>1D']

            raiz_afeta = df.pivot_table(columns=['Último Raiz'], aggfunc='size')
            raiz_afeta = raiz_afeta.drop(0, axis=0)

            base = raiz_afeta.to_dict()
            raiz_afeta = []

            for i in range(len(df)):
                raiz = df.iloc[i]['Último Raiz']
                raiz_afeta.append(base.get(raiz) if raiz in base.keys() else 0)

            df['Raiz Afeta'] = raiz_afeta

            del df['Regional'], df['Área'], df['Tecnologia']

            df = df.rename(columns={'Área Responsável': 'Time', 'Grupo Responsável': 'Responsável', 'Sigla ERB': 'ERB',
                                    'Último Raiz': 'Raiz', 'Tempo': 'Tempo Baixa',
                                    'Tipo Bilhete.1': 'Tipo Bilhete Raiz'})

            df.insert(3, 'Localidade', df.pop('Localidade'))
            df['Responsável'] = df.pop('Responsável')
            df['Time'] = df.pop('Time')

            just_acao = []
            just_acao_user = []
            for i in range(len(df)):
                ta = df.iloc[i]
                txt = ''

                if ta['Raiz'] != 0:
                    if ta['Tempo Baixa'] == '<=4h':
                        txt = 'Raiz Aguardando Atuação (Esperado)'
                    elif 'ASTRO PERSISTENCIA' in str(ta['Tipo Bilhete Raiz']):
                        if ta['Tempo Baixa'] in ['>365D', '>180D', '>90D', '>30D', '>7D', '>3D', '>1D']:
                            txt = 'Raiz Aguardando Atuação (Fora do Prazo)'
                    elif ta['Tipo Bilhete Raiz'] == 'ASTRO DOL':
                        if ta['Tempo Baixa'] == '>4h':
                            txt = 'Raiz Aguardando Atuação (Esperado)'
                    elif ta['Responsável'] in ['Eventos S1', 'Eventos IUB']:
                        txt = 'TA no Fluxo SONAR'
                    elif ta['Responsável'] == 'NOC MG Desempenho On Line_Retenção':
                        txt = 'Raiz em Atuação'

                if txt == '':
                    if ta['Responsável'] in ['Automacao', 'AUTOMACAO NOC', 'NOC MG Astro',
                                             'ERB Sem Cadastro/Não Ativo']:
                        txt = 'TA na Responsabilidade da Automação'
                    elif ta['Responsável'] == 'NOC MG Desempenho On Line_Retenção':
                        txt = 'TA em Atuação'

                just_acao.append(txt)
                just_acao_user.append('SYSTEM' if txt != '' else '')

            df['Justificativa / Ação'] = just_acao
            df['Analista'] = just_acao_user

            fileloc = backlog_fileloc(agora.timestamp())
            df.to_excel(fileloc)

            aws_client().upload_file(fileloc, BUCKET,
                                     DOWNLOAD_FOLDER.replace("\\", "/") + "/" + backlog_filename(agora.timestamp()))
        except Exception as e:
            raise e
        finally:
            if os.path.exists(temp_save_path):
                os.remove(temp_save_path)

    except Exception as e:
        return render_template('500.html', e=e), 500

    return "", 200


def backlog_filename(time: float):
    time = datetime.fromtimestamp(time)
    nome_arquivo = f'Backlog NOC ' \
                   f'{time.day:02}{time.month:02}{time.year} ' \
                   f'{time.hour:02}{time.minute:02} {int(time.timestamp())}' \
                   f'.xlsx'
    return nome_arquivo


def backlog_fileloc(time: float, temp=False):
    nome_arquivo = backlog_filename(time)
    return os.path.join(os.getcwd(), DOWNLOAD_TEMP_FOLDER if temp else DOWNLOAD_FOLDER, nome_arquivo)
