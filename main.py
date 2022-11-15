# SETA TAMANHO DA JANELA DO KIVY (COMENTE PARA DEPLOY)
from kivy.config import Config
Config.set('graphics', 'width', '490')
Config.set('graphics', 'height', '780')

# REPOSICIONA TELA PARA O TECLADO ANDROID/IOS NAO PASSAR NA FRENTE
from kivy.core.window import Window
Window.keyboard_anim_args = {'d': .2, 't': 'in_out_expo'}
Window.softinput_mode = "below_target"

# GERENCIAMENTO DE ARQUIVOSPASTAS E ENTRADA TECLADO
from kivy.core.window import Window
from kivymd.uix.filemanager import MDFileManager

from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen
from kivymd.uix.bottomsheet import MDListBottomSheet
from telas import *
from botoes import *
from datetime import date
from bannerlist import BannerList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton
from myfirebase import MyFirebase
from zerartelas import ZerarTelas
import requests
import certifi
import os

# CERTIFICADO DATABASE FIREBASE
os.environ["SSL_CERT_FILE"] = certifi.where()

# ARQUIVO DAS TELAS KV
doc_main_kv = "main.kv"

class MainApp(MDApp):
    # Define a caixa de dialogo como None
    dialog = None
    list_chaves = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path
        )

    def build(self):
        """ Inicia database, telas Kv e define o tema do App """
        self.firebase = MyFirebase()
        self.root = Builder.load_file(doc_main_kv)
        self.tema("Dark", "Orange")

    def on_start(self):
        """ Carrega as pré-definições do App """
        self.carregar_infos_usuario()
        # DEFINE O ANO E MES NOS BOTOES DE REFERENCIA
        mes_e_ano = self.pegar_mes()
        self.definir_mes(mes_e_ano[1])
        self.definir_ano(mes_e_ano[2])

    def tema(self, tema, botoes):
        '''
        Configura temas de tela pré-definidos no Kivy.
        :param tema (str): Opções de tela Dark ou Light;
        :param botoes (str): Opções de cores: 'Red', 'Pink', 'Purple', 'DeepPurple', 'Indigo', 'Blue', 'LightBlue', 'Cyan',
        'Teal', 'Green', 'LightGreen', 'Lime', 'Yellow', 'Amber', 'Orange', 'DeepOrange', 'Brown', 'Gray', 'BlueGray'
        '''
        self.theme_cls.theme_style = tema
        self.theme_cls.primary_palette = botoes

        MDScreen()

    def carregar_infos_usuario(self):
        ''' Carrega as predefinições dos usuários '''
        try:
            # Verifica se o usuário tem refresh token para mantê-lo logado
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()

            # Atualiza os tokens com REST API
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # Requisição do perfil do usuário no database
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{local_id}"
                                      f".json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            # Carrega fotos e nomes dos usuários
            foto_user1 = requisicao_dic["foto_user1"].replace("+", "\\")
            foto_user2 = requisicao_dic["foto_user2"].replace("+", "\\")
            self.nome_user1 = requisicao_dic["nome_user1"]
            self.nome_user2 = requisicao_dic["nome_user2"]
            # Seta os dados na tela de homepage
            pagina = self.root.ids["homepage"]
            pagina.ids["foto_perfil_user1"].source = f'{foto_user1}'
            pagina.ids["foto_perfil_user2"].source = f'{foto_user2}'
            pagina.ids["acoes_user1"].text = self.nome_user1
            pagina.ids["acoes_user2"].text = self.nome_user2
            pagina = self.root.ids["fotoperfilpage"]
            pagina.ids["foto_perfil_user1"].source = f'{foto_user1}'
            pagina.ids["foto_perfil_user2"].source = f'{foto_user2}'
            # Vai para homepage
            self.mudar_tela("homepage")
        except Exception as ex:
            # toast("Erro (info users)")
            pass

    def seta_nomes_usuarios(self):
        """ Seta os nomes de usuários na janela de configurações de nomes """
        self.enviar_parametro(pag="usernamepage", id="nome_user1", par="text", dado=self.nome_user1)
        self.enviar_parametro(pag="usernamepage", id="nome_user2", par="text", dado=self.nome_user2)
        self.mudar_tela('usernamepage')

    def alterar_nome_usuarios(self, nome_user1, nome_user2):
        '''
        Altera os nomes de usuários nas telas de exibição e salva no database.
        :param nome_user1 (str):  Nome do usuário 1;
        :param nome_user2 (str): Nome do usuário 2;
        '''
        if nome_user1 and nome_user2:
            # PEGA TEXT DOS INPUTS E SETA 1A LETRA MAIUSCULA
            nome_user1 = nome_user1.title()
            nome_user2 = nome_user2.title()
            # SALVA NOMES NO BD
            link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
            info = f'{{"nome_user1": "{nome_user1}", "nome_user2": "{nome_user2}"}}'
            requests.patch(link, data=info)
            # SETA NOMES DE USUÁRIOS NA HOMEPAGE
            pagina_home = self.root.ids["homepage"]  # pega pagina pelo id
            pagina_home.ids["acoes_user1"].text = nome_user1
            pagina_home.ids["acoes_user2"].text = nome_user2
            # SETA NOVOS USUÁRIOS
            self.nome_user1 = nome_user1
            self.nome_user2 = nome_user2
            # VAI PARA HOMEPAGE
            self.mudar_tela("homepage")
        else:
            toast("Preencha todos os nomes!")

    def abrir_lista_opcoes(self, menu):
        '''
        Abre a lista de opções do botão clicado e executa a ação desejada.
        :param menu (str): Nome do menu vindo do botão KV;
        '''
        # Lista de itens do menu que será escolhido
        menu_itens = []

        if menu == "menu_telas":
            menu_itens = ["Configurações"]
            function = self.acoes_menu

        elif menu == "menu_mes":
            mes_dic = self.pegar_mes()
            menu_itens = list(mes_dic[3].values())
            function = self.definir_mes

        elif menu == "menu_ano":
            for ano in range(2022, 2031):
                menu_itens.append(ano)
            function = self.definir_ano

        elif menu == "menu_user1":
            menu_itens = [f"[color=#00CFDB]Menu {self.nome_user1}[/color]", "Cadastrar despesas", "Ver minhas despesas",
                          "Cadastrar contas fixas", "Relatórios"]
            function = self.acoes_user
            self.user_atual = self.nome_user1

        elif menu == "menu_user2":
            menu_itens = [f"[color=#00CFDB]Menu {self.nome_user2}[/color]", "Cadastrar despesas", "Ver minhas despesas",
                          "Cadastrar contas fixas", "Relatórios"]
            function = self.acoes_user
            self.user_atual = self.nome_user2

        bottom_sheet_menu = MDListBottomSheet()
        for i in range(0, len(menu_itens)):
            if menu_itens[i] == "aluguelpage":
                bottom_sheet_menu.add_item(f"{menu_itens[i]}", lambda x, y=i: self.ver_aluguel())
            else:
                bottom_sheet_menu.add_item(f"{menu_itens[i]}", lambda x, y=i: function(f"{menu_itens[y]}"))
        bottom_sheet_menu.open()

    def acoes_user(self, acao):
        '''
        Executa a ação do item escolhido no menu de opções
        :param acao (str): Representa o nome da ação escolhida no menu;
        '''

        if acao == "Cadastrar despesas":
            self.pagar_conta(self.user_atual)
        if acao == "Ver minhas despesas":
            credor = self.pegar_credor(self.user_atual)
            self.preencher_banner(self.user_atual, self.mes_ref, self.ano_ref, credor)
        if acao == "Cadastrar contas fixas":
            self.ver_aluguel()
        if acao == "Relatórios":
            user_2 = self.pegar_credor(self.user_atual)
            self.relatorio_pagamento(self.user_atual, user_2)

    def acoes_menu(self, acao):
        '''
        Executa a ação do item escolhido no menu de opções
        :param acao (str): Representa o nome da ação escolhida no menu;
        '''
        if acao == "Configurações":
            self.mudar_tela("configpage")

    def pegar_credor(self, user_atual):
        '''
        Pega nome do usuário oposto chamado de credor
        :param user_atual (str): Nome do usuário logado;
        :return credor (str): Nome do usuário oposto (credor)
        '''
        if user_atual == self.nome_user1:
            credor = self.nome_user2
        else:
            credor = self.nome_user1
        return credor

    def calcular_resumo_cf(self):
        """ Calcula o resumo das despesas de acordo com os CHECKBOXs escolhidos """
        try:
            # PEGA OS CAMPOS SETADOS PELO USUÁRIO
            pagina_aluguel = self.root.ids["aluguelpage"]
            aluguel_vl = pagina_aluguel.ids["preco_aluguel"].text.replace(",", ".")
            condominio_vl = pagina_aluguel.ids["preco_condominio"].text.replace(",", ".")
            agua_vl = pagina_aluguel.ids["preco_agua"].text.replace(",", ".")
            agua_inclusa = pagina_aluguel.ids["check_agua"].active
            cond_inclusa = pagina_aluguel.ids["check_cond"].active
            # FLOAT GARANTE QUE O USUARIO ESTA DIGITANDO UM NUMERAL OU CAIRÁ NO EXCEPT
            aluguel = float(aluguel_vl)
            condominio = float(condominio_vl)
            agua = float(agua_vl)

            if aluguel != "" and condominio != "" and agua != "":
                if cond_inclusa or agua_inclusa:
                    if cond_inclusa and not agua_inclusa:
                        pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel:.2f}"
                        pagina_aluguel.ids[
                            "label_cond"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(condominio):.2f})"
                        pagina_aluguel.ids["label_agua"].text = f"Água a pagar: R$ {agua:.2f}"
                        condominio = 0
                    if agua_inclusa:
                        if cond_inclusa:
                            pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel:.2f}"
                            pagina_aluguel.ids["label_cond"].text = f"Agua e condominio incluso"
                            pagina_aluguel.ids[
                                "label_agua"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(condominio) - float(agua):.2f})"
                            agua = 0
                            condominio = 0
                        else:
                            pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel:.2f}"
                            pagina_aluguel.ids["label_cond"].text = f"Condominio a pagar: R$ {condominio:.2f}"
                            pagina_aluguel.ids[
                                "label_agua"].text = f"(Valor real aluguel: R$ {float(aluguel) - float(agua):.2f})"
                            agua = 0
                else:
                    pagina_aluguel.ids["label_aluguel"].text = f"Aluguel a pagar: R$ {aluguel:.2f}"
                    pagina_aluguel.ids["label_cond"].text = f"Condominio a pagar: R$ {condominio:.2f}"
                    pagina_aluguel.ids["label_agua"].text = f"Água a pagar: R$ {agua:.2f}"
                self.gravar_pag_aluguel(aluguel_vl, condominio_vl, agua_vl, aluguel, condominio, agua)
            else:
                toast("Cadastre todos os valores!")
        except Exception as ex:
            toast("Cadastre todos os valores corretamente!")

    def gravar_pag_aluguel(self, *args):
        '''
        Grava no database os valores de aluguel, condomínio e água.
        :param args (float):  valores Aluguel, condomínio e água respectivamente;
        '''

        # CAMPO PARA URL DB
        campo = self.mes_ref + "_" + self.ano_ref
        # VERIFICA CHECKBOX AGUA E CONDOMINIO SE INCLUSO
        check_agua = self.pegar_parametro(pag="aluguelpage", id="check_agua", par="active")
        check_cond = self.pegar_parametro(pag="aluguelpage", id="check_cond", par="active")
        # CADASTRA VALORES NO DATABASE
        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}"
        info = f'{{"aluguel": "{args[0]}", "condominio": "{args[1]}", "agua": "{args[2]}", "aluguel_ttl": "{args[3]}",' \
               f' "condominio_ttl": "{args[4]}", "agua_ttl": "{args[5]}", "check_agua": "{check_agua}",' \
               f'"check_cond": "{check_cond}"}}'
        requests.patch(link, data=info)

    def ver_aluguel(self):
        """ Mostra na tela os valores de aluguel, água e condomínio cadastrado no banco de dados"""
        ZerarTelas.zerar_contasfixas(self)
        campo = self.mes_ref + "_" + self.ano_ref

        try:
            # REQUISICAO DE VALORES DAS CONTAS FIXAS NO DB
            requisicao = requests.get(
                f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/"
                f"{campo}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            # COLHER VALORES VINDO NO DICT JSON
            cond = requisicao_dic["condominio"]
            aluguel = requisicao_dic["aluguel"]
            agua = requisicao_dic["agua"]
            check_cond = requisicao_dic["check_cond"]
            check_agua = requisicao_dic["check_agua"]

            aluguel = float(aluguel)
            cond = float(cond)
            agua = float(agua)

            if check_cond == "True":
                cond_ative = True
            else:
                cond_ative = False
            if check_agua == "True":
                agua_ative = True
            else:
                agua_ative = False

            self.enviar_parametro(pag="aluguelpage", id="label_aviso_aluguel", par="text",
                                  dado=f"[color=#000000]Cadastro de: {self.mes_ref}/{self.ano_ref}[/color]")
            self.enviar_parametro(pag="aluguelpage", id="preco_aluguel", par="text", dado=str(f"{aluguel:.2f}"))
            self.enviar_parametro(pag="aluguelpage", id="preco_condominio", par="text", dado=str(f"{cond:.2f}"))
            self.enviar_parametro(pag="aluguelpage", id="preco_agua", par="text", dado=str(f"{agua:.2f}"))
            self.enviar_parametro(pag="aluguelpage", id="check_agua", par="active", dado=agua_ative)
            self.enviar_parametro(pag="aluguelpage", id="check_cond", par="active", dado=cond_ative)

            # IR PARA PAGINA ALUGUELPAGE
            self.mudar_tela("aluguelpage")
        except Exception as ex:
            self.mudar_tela("aluguelpage")
            # print(ex)

    def pagar_conta(self, usuario):
        '''
        Vai para tela pagarpage, mas antes verifica as contas pagas e em aberto para exibi-las
        :param usuario (str): Nome do usuário logado;
        '''
        # RESET CAMPOS DE PAGARPAGE
        ZerarTelas.zerar_telapagar(self)
        # PEGAR DATA ATUAL
        data_now = self.pegar_mes()
        # RESET CAMPOS DE PAGAMENTOS
        ZerarTelas.zerar_pagamentos(self)
        # PREENCHE A TELA SCROOLPAGE
        self.ver_status_contas()
        # SETA CAMPOS DA PAGINA
        self.enviar_parametro(pag="pagarpage", id="label_aviso_pago", par="text",
                              dado=f"[color=#000000]Despesas: {self.user_atual}[/color]")
        self.enviar_parametro(pag="pagarpage", id="lbl_mes_referencia", par="text",
                              dado=f"[color=#000000]{self.mes_ref}/{self.ano_ref}[/color]")
        self.enviar_parametro(pag="pagarpage", id="input_data", par="text", dado=data_now[0])
        # SETA CAMPO DA URL DE REQUISICAO
        campo = self.mes_ref + "_" + self.ano_ref
        try:
            # REQUISICAO DB
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text",
                                  dado=f"[color=#00CFDB]Contas fixas: {self.mes_ref}[/color]")
            requisicao = requests.get(
                f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/aluguel/{campo}.json?auth={self.id_token}")
            requisicao_dic = requisicao.json()
            # pegar valores database
            agua = requisicao_dic["agua_ttl"]
            cond = requisicao_dic["condominio_ttl"]
            alug = requisicao_dic["aluguel_ttl"]
            # PREENCHER OS CAMPOS DA TELA PAGARPAGE
            self.enviar_parametro(pag="pagarpage", id="lbl_alg_status", par="text", dado=f"Aluguel: R${alug}")
            self.enviar_parametro(pag="pagarpage", id="lbl_cond_status", par="text", dado=f"Cond.: R${cond}")
            self.enviar_parametro(pag="pagarpage", id="lbl_agua_status", par="text", dado=f"Agua: R${agua}")
            # DEFINE OS BOTOES PAGAR OU INCLUSO NA TELA PAGARPAGE
            if alug == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Incluso")
            if cond == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Incluso")
            if agua == "0":
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Incluso")
        except:
            self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
            self.enviar_parametro(pag="pagarpage", id="label_aviso", par="text",
                                  dado=f"[color=#00CFDB]Cadastre contas de {self.mes_ref}[/color]")
            toast("Contas fixas ainda não cadastradas!")
        credor = self.pegar_credor(usuario)
        self.enviar_parametro(pag="pagarpage", id="btn_user_credor", par="text", dado=f"Devo a {credor}")
        self.mudar_tela("pagarpage")

    def cadastrar_pagamento(self, tipo):
        '''
        Cadastra no banco de dados pagamentos ou devedor um item que será exibido no banner
        :param tipo (str): pagamento ou devedor define onde cadastrar no database
        '''
        # PEGA OS INPUTS DO USUARIO PARA FAZER A REQUISIÇÃO POST NO DB
        descricao = self.pegar_parametro(pag="pagarpage", id="input_desc", par="text").title()
        data = self.pegar_parametro(pag="pagarpage", id="input_data", par="text")
        valor = self.pegar_parametro(pag="pagarpage", id="input_valor", par="text").replace(",", ".")
        raiz = "pagamentos"
        cod_user = self.pegar_cod_ou_credor(self.user_atual)[0]
        try:
            valor = float(valor)
            if tipo == "devedor":
                raiz = "devedor"
            if descricao and data and valor:
                campo = cod_user + "_" + self.mes_ref + "_" + self.ano_ref
                # CADASTRAR DADOS
                link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/{raiz}/{campo}.json?auth={self.id_token}"
                data = f'{{"descricao": "{descricao}", "data": "{data}", "valor": "{valor}"}}'
                requests.post(link, data)
                # LIMPAR O BANNER
                self.limpar_banner()
                # PREENCHE O BANNER
                credor = self.pegar_cod_ou_credor(self.user_atual)[1]
                self.preencher_banner(self.user_atual, self.mes_ref, self.ano_ref, credor)
                # IR PARA TELA DO BANNER
                self.mudar_tela("scrollpage")
            else:
                toast("Nenhum campo pode ser vazio!")
        except Exception as ex:
            toast(f"Preencha os campos corretamente!")

    def pagar_conta_fixa(self, *args):
        '''
        Pega os valores mostrados na tela de pagamento preenche automaticamente para efetuar o pagamento
        :param args (str): Nome do campo e valor.
        :return:
        '''
        # PREENCHE OS DADOS DO BOTAO DE CONTAS FIXAS
        if args[0] == "alg":
            descricao = args[1][0:7] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Aluguel: R$", "")
        if args[0] == "cond":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Cond.: R$", "")
        if args[0] == "agua":
            descricao = args[1][0:4] + "_" + self.mes_ref + "_" + self.ano_ref
            valor = args[1].replace("Agua: R$", "")
        # PREENCHE OS AUTOMATICAMENTE CAMPOS PARA PAGAMENTO DE CONTAS FIXAS
        self.enviar_parametro(pag="pagarpage", id="input_desc", par="text", dado=descricao)
        self.enviar_parametro(pag="pagarpage", id="input_valor", par="text", dado=valor)
        # VAI PARA FUNÇÃO DE PAGAMENTO
        self.cadastrar_pagamento("pagamentos")

    def apagar_item_lista(self, user):
        '''
        Apaga items da lista do scroolpage e deleta do Database de acordo com o código do item e do respectivo usuário
        :param user (str): usuário que solicitou exclusão, dado vindo do botão kv.
        '''
        # PREENCHE O CAMPO PARA REQUISICAO DB
        cod_user = self.pegar_cod_ou_credor(self.user_atual)[0]
        campo = cod_user + "_" + self.mes_ref + "_" + self.ano_ref
        # PEGA CODIGO DO ITEM A SER EXCLUIDO
        codigo = self.pegar_parametro(pag="scrollpage", id="code_input", par="text")
        if codigo:
            for code in self.list_chaves:
                if codigo == code[1:7].replace("-", "x").lower():
                    try:
                        # PROCURA O CODIGO EM PAGAMENTOS
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/" \
                               f"{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass
                    try:
                        # PROCURA O CODIGO EM DEVEDOR
                        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/" \
                               f"{campo}/{code}.json?auth={self.id_token}"
                        requests.delete(link)
                    except:
                        pass
                    toast("Item excluido da lista!")
                    # RESETA O BANNER
                    credor = self.pegar_credor(cod_user)
                    self.limpar_banner()
                    self.preencher_banner(self.user_atual, self.mes_ref, self.ano_ref, credor)
                    self.enviar_parametro(pag="scrollpage", id="code_input", par="text", dado="")
                    break
        else:
            toast("Digite um código para excluir da lista!")

    def limpar_banner(self):
        """ Remove item excluido da lista pagamento ou lista de dividas da scroolpage """
        # REMOVE OS DADOS DA LISTA_PAGAMENTOS
        lista_pagamentos = self.pegar_parametro(pag="scrollpage", id="lista_pagamentos", par="id")
        for item in list(lista_pagamentos.children):
            lista_pagamentos.remove_widget(item)
        # REMOVE OS DADOS DA LISTA_DIVIDAS
        lista_dividas = self.pegar_parametro(pag="scrollpage", id="lista_dividas", par="id")
        for item in list(lista_dividas.children):
            lista_dividas.remove_widget(item)

    def preencher_banner(self, *args):  # recebe: usuario[0], spinner mes[1], spinner ano[2] e credor[3]
        '''
        Preenche o banner na scroolpage para consulta dos dados
        :param args (str): usuário, spinner_mes, spinner_ano e credor respectivamente;
        '''
        # LIMPA O BANNER PARA ENTRADA DE NOVOS DADOS
        self.limpar_banner()
        self.enviar_parametro(pag="scrollpage", id="code_input", par="text", dado="")
        # PREENCHE TITULO DA PAGINA DE PAGAMENTOS
        self.enviar_parametro(pag="scrollpage", id="pgmt_user", par="text",
                              dado=f"[color=#000000]Relatório de: {args[0]}[/color]")
        self.enviar_parametro(pag="scrollpage", id="pgmt_mes", par="text",
                              dado=f"[color=#000000]{args[1]}/{args[2]}[/color]")
        # REQUISCAO NO BD
        cod_user = self.pegar_cod_ou_credor(args[0])[0]
        campo = cod_user + "_" + args[1] + "_" + args[2]
        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_pagamentos = self.pegar_parametro(pag="scrollpage", id="lista_pagamentos", par="id")
        # SOMA TODOS PAGAMENTOS DA LISTA
        soma = self.publicar_banner(lista_pagamentos, requisicao_dic)
        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_pgm", par="text",
                              dado=f"[color=#00CFDB]Total despesas casa: R${soma}[/color]")

        # SOMA TODAS AS DIVIDAS DA LISTA
        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/devedor/{campo}.json?auth={self.id_token}")
        requisicao_dic = requisicao.json()
        lista_dividas = self.pegar_parametro(pag="scrollpage", id="lista_dividas", par="id")
        soma = self.publicar_banner(lista_dividas, requisicao_dic)
        if soma == None:
            soma = "0"
        else:
            soma = "{:.2f}".format(soma)
        self.enviar_parametro(pag="scrollpage", id="lbl_soma_div", par="text",
                              dado=f"[color=#00CFDB]Total devo a {args[3]}: R${soma}[/color]")
        # IR PARA TELA DE PAGAMENTOS
        self.mudar_tela("scrollpage")

    def publicar_banner(self, *args):  # recebe lista e requisicao_dic e soma
        '''
        Soma os valores da lista de pagamentos e dividas para exibir no scroolpage
        :param args (str): recebe uma lista de valores pagos ou devedor;
        :return soma(float): Retorna a soma de todos valores da lista recebina;
        '''
        soma = 0
        try:
            for local_id_user in args[1]:
                valor = args[1][local_id_user]["valor"]
                valor = float(valor)
                valor = "{:.2f}".format(valor)
                data = args[1][local_id_user]["data"]
                descricao = args[1][local_id_user]["descricao"]
                soma = soma + float(valor)
                self.list_chaves.append(local_id_user)
                code = local_id_user[1:7].replace("-", "x").lower()
                banner = BannerList(descricao=descricao[0:11] + "...", data=data, valor=valor, code=code)
                args[0].add_widget(banner)
            return soma
        except:
            pass

    def ver_status_contas(self):
        ''' Verifica as contas fixas pagas para exibir os botoes de pagamentos habilitados ou não '''
        lista = []
        try:
            campo = "user1" + "_" + self.mes_ref + "_" + self.ano_ref
            lista = self.criar_lista(campo, lista)
        except:
            pass
        try:
            campo = "user2" + "_" + self.mes_ref + "_" + self.ano_ref
            lista = self.criar_lista(campo, lista)
        except:
            pass
        # CASO ITEM NA LISTA, DESABILITA BOTAO DE PAGAMENTO
        for item in lista:
            if item == "Aluguel" + "_" + self.mes_ref + "_" + self.ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_alg_status", par="text", dado="Pago")
            if item == "Cond" + "_" + self.mes_ref + "_" + self.ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_cond_status", par="text", dado="Pago")
            if item == "Agua" + "_" + self.mes_ref + "_" + self.ano_ref:
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="disabled", dado=True)
                self.enviar_parametro(pag="pagarpage", id="btn_agua_status", par="text", dado="Pago")

    def relatorio_pagamento(self, *args):
        '''
        Calcula os valores pagos pelos usuários para exibir o relatorio em relatoriopage
        :param args: Lista com user1 e user2;
        :return:
        '''

        cod_userx = self.pegar_cod_ou_credor(args[0])[0]
        cod_usery = self.pegar_cod_ou_credor(args[1])[0]

        self.enviar_parametro(pag="relatoriopage", id="relat_mes", par="text",
                              dado=f"[color=#000000]{self.mes_ref}/{self.ano_ref}[/color]")
        self.enviar_parametro(pag="relatoriopage", id="lbl_rel_user1", par="text", dado=f"Relatório de {args[0]}:")
        self.enviar_parametro(pag="relatoriopage", id="lbl_rel_user2", par="text", dado=f"Relatório de {args[1]}:")

        # pegar pagamentos para user1
        total1 = self.pegar_total_pago(cod_userx, self.mes_ref, self.ano_ref, "pagamentos")
        self.enviar_parametro(pag="relatoriopage", id="lbl_pago_user1", par="text", dado=f"Despesas: R${total1:,.2f}")
        # pegar pagamentos para user2
        total2 = self.pegar_total_pago(cod_usery, self.mes_ref, self.ano_ref, "pagamentos")
        self.enviar_parametro(pag="relatoriopage", id="lbl_pago_user2", par="text", dado=f"Despesas: R${total2:,.2f}")

        total_despesas = total1 + total2
        ttl_cada = total_despesas / 2
        self.enviar_parametro(pag="relatoriopage", id="lbl_ttl_desp", par="text",
                              dado=f"Total despesas: R${total_despesas:,.2f}")
        self.enviar_parametro(pag="relatoriopage", id="lbl_ttl_cada", par="text",
                              dado=f"Total pra cada: R${total_despesas / 2:,.2f}")

        # pegar pagamentos para user1
        total3 = self.pegar_total_pago(cod_userx, self.mes_ref, self.ano_ref, "devedor")
        self.enviar_parametro(pag="relatoriopage", id="lbl_dev_user1", par="text",
                              dado=f"Deve a {args[1]}: R${total3:,.2f}")
        # pegar pagamentos para user2
        total4 = self.pegar_total_pago(cod_usery, self.mes_ref, self.ano_ref, "devedor")
        self.enviar_parametro(pag="relatoriopage", id="lbl_dev_user2", par="text",
                              dado=f"Deve a {args[0]}: R${total4:,.2f}")

        if ttl_cada < total1:  # dsa deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"{args[1]} deve a {args[0]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"R${(total1 - ttl_cada):,.2f}")
        elif ttl_cada < total2:  # za deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"{args[0]} deve a {args[1]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"R${(total2 - ttl_cada):,.2f}")
        else:
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeve", par="text",
                                  dado=f"Não á débtos!")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deve", par="text",
                                  dado=f"")

        if total4 < total3:  # dsa deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"{args[0]} deve a {args[1]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"R${(total3 - total4):,.2f}")
        elif total3 < total4:  # za deve
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"{args[1]} deve a {args[0]}:")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"R${(total4 - total3):,.2f}")
        else:
            self.enviar_parametro(pag="relatoriopage", id="lbl_quemdeveind", par="text",
                                  dado=f"Não há débito!")
            self.enviar_parametro(pag="relatoriopage", id="lbl_vl_deveind", par="text",
                                  dado=f"")

        self.mudar_tela("relatoriopage")

    def pegar_total_pago(self, *args):
        '''
        Calcula o total pago pelo usuário solicitado de acordo com mes e ano
        :param args: recebe user, mes, ano e raiz;
        :return total: retorna total pago pelo usuario no mes e ano solicitado;
        '''
        total = 0
        try:
            campo = args[0] + "_" + args[1] + "_" + args[2]
            requisicao = requests.get(f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}"
                                      f"/{args[3]}/{campo}.json?auth={self.id_token}")
            dic = requisicao.json()

            for valor in dic:
                total = total + float((dic[valor]["valor"]))
            return total
        except:
            return total

    def criar_lista(self, campo, lista):
        '''
        Cria a lista de pagametos realizados pelo usuário por mes e ano
        :param campo (str): Parte da URL do database referente ao usuario solicitado;
        :param lista (lista): Lista que será adicionada todos os pagamentos do user1 e user2;
        :return lista: retorna a lista de pagamentos;
        '''
        requisicao = requests.get(
            f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}/pagamentos/{campo}.json?auth={self.id_token}")
        dic = requisicao.json()
        for valor in dic:
            lista.append(dic[valor]["descricao"])
        return lista

    def show_alert_dialog(self):
        """ Caixa de dialogo sair da conta, remove o token que mantem usúario logado e sai da conta"""
        self.dialog = ""
        if not self.dialog:
            self.dialog = MDDialog(
                # title="Atenção!",
                text="Sair da conta?",
                buttons=[
                    MDFlatButton(
                        text="Cancelar",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.fechar_tela
                    ),
                    MDRectangleFlatButton(
                        text="Sim",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.opcao
                    ),
                ],
            )
        self.dialog.open()

    def fechar_tela(self, obj):
        """ Fecha a caixa de dialogo"""
        self.dialog.dismiss()

    def opcao(self, obj):
        """ Faz logoff removendo o token que mantinha usuário logado"""
        self.dialog.dismiss()
        self.fazer_logoff()

    def fazer_logoff(self):
        """ Remove o token de usuário logado """
        path = os.path.join("refreshtoken.txt")
        os.remove(path)
        self.mudar_tela("loginpage")

    def mudar_tela(self, id_tela):
        '''
        Função que muda para tela solicitada de acordo com seu ID
        :param id_tela (str): ID da tela solicitada;
        '''
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def pegar_cod_ou_credor(self, usuario):
        '''
        Pega o código e o nome do usuário oposto (credor)
        :param usuario (str): Nome do usuário que esta solicitando;
        :returns
            cod_user (str): retorna código do usuário que esta solicitando;
            credor (str): retorna o nome do usuário oposto (credor);
        '''
        if usuario == self.nome_user1:
            cod_user = "user1"
            credor = self.nome_user2
        else:
            cod_user = "user2"
            credor = self.nome_user1
        return cod_user, credor

    def enviar_parametro(self, pag, id, par, dado):
        '''
        Envia um parâmetro para um item da página KV solicitada;
        :param pag (str): Nome da página;
        :param id (str): Id da página;
        :param par (str): Parametro que deseja mudar text, color, hint_text, active, disable ou source;
        :param dado (str): Dado a ser setado no item (ex: par=color dado=preto);
        '''
        tela = self.root.ids[pag]
        if par == "text":
            tela.ids[id].text = dado
        if par == "color":
            tela.ids[id].color = dado
        if par == "hint_text":
            tela.ids[id].hint_text = dado
        if par == "active":
            tela.ids[id].active = bool(dado)
        if par == "disabled":
            tela.ids[id].disabled = bool(dado)
        if par == "source":
            tela.ids[id].source = dado

    def pegar_parametro(self, pag, id, par):
        '''
        Pega um parâmetro da página KV solicitada.
        :param pag (str): Nome da página solicitada;
        :param id (str): ID da página solicitada;
        :param par (str): Parametro que deseja pegar text, active ou id de algum item na página;
        :return (str): Retorna o dado solicitado do item KV
        '''
        tela = self.root.ids[pag]
        if par == "text":
            dado = tela.ids[id].text
        if par == "active":
            dado = tela.ids[id].active
        if par == "id":
            dado = tela.ids[id]
        return dado

    def definir_mes(self, mes):
        '''
        Seta o nome do botão mes para o mes escolhido da consulta
        :param mes (str): Mes escollhido pelo usuário
        '''
        btn = self.root.ids["homepage"]
        btn.ids["btn_mes"].text = mes
        self.mes_ref = mes

    def definir_ano(self, ano):
        '''
        Seta o nome do botão ano para o ano escolhido da consulta
        :param ano (str): Ano escollhido pelo usuário
        '''
        btn = self.root.ids["homepage"]
        btn.ids["btn_ano"].text = ano
        self.ano_ref = ano

    def pegar_mes(self):
        '''
        Função para facilitar o uso de datas em nosso app.
        :returns
            data (str): retorna a data de hoje;
            mes_extenso (str): retorna mes escrito por extenso;
            ano (str): retorna ano;
            mes_dic (dict): retorna um dicionario de meses do ano;
        '''
        today = date.today()
        data = today.strftime("%d/%m/%Y")
        mes = today.strftime("%m")
        ano = today.strftime("%Y")
        mes_dic = {
            "01": "Janeiro",
            "02": "Fevereiro",
            "03": "Março",
            "04": "Abril",
            "05": "Maio",
            "06": "Junho",
            "07": "Julho",
            "08": "Agosto",
            "09": "Setembro",
            "10": "Outubro",
            "11": "Novembro",
            "12": "Dezembro",
        }
        mes_extenso = mes_dic[mes]
        return data, mes_extenso, ano, mes_dic

    # FUNÇÕES ABAIXO PARA ABRIR UM ARQUIVO NO SMARTPHONE (NOSSO CASO FOTO DO USUÁRIO)
    # AINDA NÃO TOTALMENTE IMPLEMENTADO

    def file_manager_open(self, user):
        self.user_foto = user
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True

    def select_path(self, path: str):
        '''
        Função chamada quando clicado no nome do diretório ou arquivo
        :param path: Caminho para o diretório ou arquivo;
        '''

        self.exit_manager()
        if self.user_foto == "foto_user1":
            self.enviar_parametro(pag="homepage", id="foto_perfil_user1", par="source", dado=path)
            self.enviar_parametro(pag="fotoperfilpage", id="foto_perfil_user1", par="source", dado=path)
        elif self.user_foto == "foto_user2":
            self.enviar_parametro(pag="homepage", id="foto_perfil_user2", par="source", dado=path)
            self.enviar_parametro(pag="fotoperfilpage", id="foto_perfil_user2", par="source", dado=path)
        self.salvar_foto_perfil(self.user_foto, path)
        toast(path)

    def salvar_foto_perfil(self, user, caminho):
        caminho_str = str(caminho).replace("\\", "+")
        link = f"https://appcontascasa-d1359-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}"
        info = f'{{"{user}": "{caminho_str}"}}'
        requests.patch(link, data=info)

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True


MainApp().run()
