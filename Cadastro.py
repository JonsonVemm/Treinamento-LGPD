from flask import Flask, render_template, request, redirect, flash
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', '123321')  # Usa variável de ambiente

# Nome do arquivo Excel
EXCEL_FILE = 'cadastros.xlsx'
LIMITE_PARTICIPANTES = 30

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
    nome = request.form['nome']
    email = request.form['email']
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
        df = pd.DataFrame(columns=['Nome', 'Email', 'Idade', 'Data_Treinamento'])

    # Cria um dicionário com os dados
    novo_dado = {
        'Nome': nome,
        'Email': email,
        'Data_Treinamento': data_treinamento
    }

    # Adiciona o novo registro
    df = pd.concat([df, pd.DataFrame([novo_dado])], ignore_index=True)

    # Salva no Excel
    df.to_excel(EXCEL_FILE, index=False)

    flash('Inscrição realizada com sucesso!')
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)