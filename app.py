import os.path
import traceback
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, send_file
from forms import FileForm
from werkzeug.utils import secure_filename

# Criando Instancia do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThatsMySecretFuckingSuperKey'
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

# Criando rotas
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/backlog', methods=['GET', 'POST'])
def backlog():
    erro = None
    nome_arquivo = None
    df = None
    form = FileForm()

    if form.validate_on_submit():

        file = request.files[form.arquivo.name]
        if file.filename.endswith('.xls') or file.filename.endswith('.xlsx'):
            try:
                agora = datetime.now()
                temp_save_path = os.path.join(UPLOAD_FOLDER, str(int(agora.timestamp())) + '_' +
                                              secure_filename(file.filename))
                file.save(temp_save_path)

                try:
                    if file.filename.endswith('.xls'):
                        df = pd.read_html(temp_save_path, index_col='Ticket')
                        df[0].to_excel(temp_save_path.replace('.xls', '.xlsx'))
                        os.remove(temp_save_path)
                        temp_save_path = temp_save_path.replace('.xls', '.xlsx')

                    df = pd.read_excel(temp_save_path)
                except Exception as e:
                    raise e
                finally:
                    os.remove(temp_save_path)

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
                                        'Último Raiz': 'Raiz', 'Tempo': 'Tempo Baixa', 'Tipo Bilhete.1': 'Tipo Bilhete Raiz'})

                df.insert(3, 'Localidade', df.pop('Localidade'))
                df['Responsável'] = df.pop('Responsável')
                df['Time'] = df.pop('Time')

                just_acao = []
                for i in range(len(df)):
                    ta = df.iloc[i]
                    txt = ''

                    if ta['Raiz'] != '0':
                        if ta['Tempo Baixa'] == '<=4h':
                            txt = 'TA Aguardando Atuação da Raiz (Esperado)'
                        elif 'ASTRO PERSISTENCIA' in str(ta['Tipo Bilhete Raiz']):
                            if ta['Tempo Baixa'] in ['>365D', '>180D', '>90D', '>30D', '>7D', '>3D', '>1D']:
                                txt = 'TA Aguardando Atuação da Raiz (Fora do Prazo)'
                        elif ta['Tipo Bilhete Raiz'] == 'ASTRO DOL':
                            if ta['Tempo Baixa'] == '>4h':
                                txt = 'TA Aguardando Atuação da Raiz (Esperado)'

                    if txt == '':
                        if ta['Responsável'] in ['Automacao', 'AUTOMACAO NOC', 'NOC MG Astro', 'ERB Sem Cadastro/Não Ativo']:
                            txt = 'TA na Responsabilidade da Automação'
                        elif ta['Responsável'] in ['Eventos S1', 'Eventos IUB']:
                            txt = 'TA no Fluxo SONAR'
                        elif ta['Responsável'] == 'NOC MG Desempenho On Line_Retenção':
                            txt = 'TA Aguardando Atuação da Raiz (Esperado)'

                    just_acao.append(txt)

                df['Justificativa / Ação'] = just_acao

                nome_arquivo = f'Backlog NOC ' \
                               f'{agora.day:02}{agora.month:02}{agora.year} ' \
                               f'{agora.hour:02}{agora.minute:02} {int(agora.timestamp())}'
                df.to_excel(os.path.join(UPLOAD_FOLDER, nome_arquivo))
            except Exception as e:
                df = None
                erro = str(e)
                print('! Deu erro:', e, flush=True)
                traceback.print_tb(e.__traceback__)
        else:
            erro = 'Tipo do arquivo não é compativel'

    return render_template('backlog.html', form=form, erro=erro, idfile=nome_arquivo, df=df)

@app.route('/download_backlog/<idfile>')
def download_backlog(idfile):
    return send_file(os.path.join(UPLOAD_FOLDER, idfile))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_internal_error(e):
    return render_template('500.html'), 500
