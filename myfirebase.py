import requests
# importa a classe app prapoder rodar os comandos do meu app
from kivymd.app import MDApp


class MyFirebase():
    API_KEY = "AIzaSyAWPCSptT1xq75isxsNpzXKl32rxPPF8i0"

    def criar_conta(self, email, senha):
        # no link do API REST vamos substituir nossa chave
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}"
        # criar um dicionario com as informacoes que o google exige (email, password e return secure)
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        # agora montar a requisicao e envia e recebe resposta
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        # pegando as messagens de erro pra printar na tela do app
        # ou se der certo pegamos as chaves
        if requisicao:

            # requisicao_dic["idToken"] #autenticacao de restrincao
            # requisicao_dic["refreshToken"] #token que mantem usuario logado,salva num arquivo e se loga automatico
            # requisicao_dic["localId"] #id do usuario, o codigo que vai identificar a pessoa

            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            # mandar as variaveis acima para o APP no main.py pra usa-los la
            meu_aplicativo = MDApp.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token

            # salvar o refresh token num arquivo txt para login automatico futuramente
            with open("refreshtoken.txt", "w") as arquivo:  # cria e escreve num txt
                arquivo.write(refresh_token)

            #data, mes, ano, mes_dic = meu_aplicativo.pegar_mes()

            # link pro firebase é em texto, com id do usuario ja ira criar o primeiro id
            link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
            info = f'{{"nome_user1": "user1", "nome_user2": "user2", "foto_user1": "fotos//user1.png", "foto_user2": "fotos//user2.png"}}'


            # na criacao do BD use sempre o patch e passe o token do usuario
            # ou ele vai criar automaticamente e ficaremos com 2
            requests.patch(link, data=info)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("usernamepage")


        else:
            msg_erro = requisicao_dic["error"]["message"]
            # pega as funcoes do APP no maim.py pra poder rodar o root
            meu_aplicativo = MDApp.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = msg_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)

    def fazer_login(self, email, senha):

        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        # criar um dicionario com as informacoes que o google exige (email, password e return secure)
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        # agora montar a requisicao e envia e recebe resposta
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao:
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]


            # mandar as variaveis acima para o APP no main.py pra usa-los la
            meu_aplicativo = MDApp.get_running_app()
            meu_aplicativo.local_id = local_id
            meu_aplicativo.id_token = id_token


            # salvar o refresh token num arquivo txt para login automatico futuramente
            with open("refreshtoken.txt", "w") as arquivo:  # cria e escreve num txt
                arquivo.write(refresh_token)

            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")

        else:
            msg_erro = requisicao_dic["error"]["message"]
            # pega as funcoes do APP no mais.py pra poder rodar o root
            meu_aplicativo = MDApp.get_running_app()
            pagina_login = meu_aplicativo.root.ids["loginpage"]
            pagina_login.ids["mensagem_login"].text = msg_erro
            pagina_login.ids["mensagem_login"].color = (1, 0, 0, 1)

    def trocar_token(self, refresh_token):

        # API REST trocar um token de atualizacao por um id
        link = f"https://securetoken.googleapis.com/v1/token?key={self.API_KEY}"

        info = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }

        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        local_id = requisicao_dic["user_id"]
        id_token = requisicao_dic["id_token"]

        return local_id, id_token

    def redefinir_senha(self, email):

        app = MDApp.get_running_app()

        # no link do API REST vamos mandar solicitação de redefinição de senha
        link = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={self.API_KEY}"
        # criar um dicionario com as informacão que o google exige (email)
        info = {"requestType":"PASSWORD_RESET",
                "email": email}
        # agora montar a requisicao e envia e recebe resposta
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao:
            app.mudar_tela("loginpage")
        else:
            msg_erro = requisicao_dic["error"]["message"]
            # pega as funcoes do APP no main.py pra poder rodar o root

            app.enviar_parametro(pag="redefinirsenha", id="lbl_aviso", par="text", dado=msg_erro)
            app.enviar_parametro(pag="redefinirsenha", id="lbl_aviso", par="color", dado=(1, 0, 0, 1))

    def excluir_conta(self, email, senha):

        app = MDApp.get_running_app()

        link = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}"
        # criar um dicionario com as informacoes que o google exige (email, password e return secure)
        info = {"email": email,
                "password": senha,
                "returnSecureToken": True}
        # agora montar a requisicao e envia e recebe resposta
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()

        if requisicao:
            refresh_token = requisicao_dic["refreshToken"]
            local_id = requisicao_dic["localId"]
            id_token = requisicao_dic["idToken"]

            # no link do API REST vamos mandar solicitação de redefinição de senha
            link = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={self.API_KEY}"
            # criar um dicionario com as informacão que o google exige (email)
            info = {"idToken": id_token}
            # agora montar a requisicao e envia e recebe resposta
            requisicao2 = requests.post(link, data=info)
            requisicao_dic = requisicao.json()

            if requisicao2:
                link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}"
                requests.delete(link)
                app.mudar_tela("loginpage")
            else:
                msg_erro = requisicao_dic["error"]["message"]
                # pega as funcoes do APP no main.py pra poder rodar o root

                app.enviar_parametro(pag="excluirconta", id="mensagem_excluir", par="text", dado=msg_erro)
                app.enviar_parametro(pag="excluirconta", id="mensagem_excluir", par="color", dado=(1, 0, 0, 1))
        else:
            msg_erro = requisicao_dic["error"]["message"]
            # pega as funcoes do APP no main.py pra poder rodar o root

            app.enviar_parametro(pag="excluirconta", id="mensagem_excluir", par="text", dado=msg_erro)
            app.enviar_parametro(pag="excluirconta", id="mensagem_excluir", par="color", dado=(1, 0, 0, 1))




