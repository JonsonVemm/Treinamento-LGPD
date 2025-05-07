from flask import Flask, render_template, request, redirect, flash, send_file, render_template_string
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '123321')  # Usa variável de ambiente

# Nome do arquivo Excel
EXCEL_FILE = 'cadastros.xlsx'
LIMITE_PARTICIPANTES = 30
UPLOAD_PASSWORD = "minhasenha123"  # Troque para uma senha forte!

# Rota principal
@app.route('/')
def index():
    # Carrega as inscrições existentes para mostrar vagas disponíveis
    vagas_disponiveis = {}
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        for data in df['Data_Treinamento'].unique():
            inscritos = len(df[df['Data_Treinamento'] == data])
            vagas_disponiveis[data] = LIMITE_PARTICIPANTES - inscritos
    return render_template('form.html', vagas_disponiveis=vagas_disponiveis)

# Rota que recebe os dados do formulário
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    try:
        nome = request.form['nome']
        email = request.form['email']
        setor = request.form['setor']
        gestor = request.form['gestor']
        data_treinamento = request.form['data_treinamento']

        # Verifica se já existe o arquivo Excel
        if os.path.exists(EXCEL_FILE):
            df = pd.read_excel(EXCEL_FILE)
            
            # Verifica se já atingiu o limite para a data selecionada
            inscritos_data = len(df[df['Data_Treinamento'] == data_treinamento])
            if inscritos_data >= LIMITE_PARTICIPANTES:
                flash(f'Desculpe, todas as vagas para a data {data_treinamento} já foram preenchidas.')
                return redirect('/')
        else:
            df = pd.DataFrame(columns=['Nome', 'Email', 'Setor', 'Gestor', 'Data_Treinamento'])

        # Cria um dicionário com os dados
        novo_dado = {
            'Nome': nome,
            'Email': email,
            'Setor': setor,
            'Gestor': gestor,
            'Data_Treinamento': data_treinamento
        }

        # Adiciona o novo registro
        df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)

        # Salva no Excel
        df.to_excel(EXCEL_FILE, index=False)

        flash('Inscrição realizada com sucesso!')
        return redirect('/')
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")  # Isso vai aparecer nos logs do Render!
        flash('Erro ao realizar inscrição')
        return redirect('/')

@app.route('/baixar-cadastros')
def baixar_cadastros():
    if os.path.exists(EXCEL_FILE):
        return send_file(EXCEL_FILE, as_attachment=True)
    else:
        return "Nenhum cadastro encontrado.", 404

@app.route('/upload-cadastros', methods=['GET', 'POST'])
def upload_cadastros():
    if request.method == 'POST':
        senha = request.form.get('senha')
        arquivo = request.files.get('arquivo')
        if senha != UPLOAD_PASSWORD:
            return "Senha incorreta!", 403
        if arquivo and arquivo.filename.endswith('.xlsx'):
            arquivo.save(EXCEL_FILE)
            return "Arquivo enviado com sucesso!"
        else:
            return "Envie um arquivo .xlsx válido.", 400

    # Formulário simples de upload
    return render_template_string('''
        <h2>Upload de cadastros.xlsx</h2>
        <form method="post" enctype="multipart/form-data">
            Senha: <input type="password" name="senha"><br>
            Arquivo: <input type="file" name="arquivo" accept=".xlsx"><br>
            <input type="submit" value="Enviar">
        </form>
    ''')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
