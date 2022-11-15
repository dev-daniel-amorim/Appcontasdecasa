<h1 align="center"> App Contas de casa </h1>
 
 <p align="center">
<img src="https://user-images.githubusercontent.com/115194365/201988258-1c86e314-28ef-4889-9253-df1b8a752e4f.png"/>
</p>


# Índice 

* [Descrição do Projeto](#descrição-do-projeto)
* [Status](#status)
* [Funcionalidades e Demonstração da Aplicação](#funcionalidades-e-demonstração-da-aplicação)
* [Tecnologias utilizadas](#tecnologias-utilizadas)
* [Desenvolvedor](#desenvolvedor)
* [Considerações Finais](#considerações-finais)
* [Tutorial Deploy](#tutorial-deploy)

# Descrição do projeto
 App para Android e Ios para controle (até 2 pessoas) de contas pessoais mensais como
 água, energia, aluguel, condominio e despesas gerais de casa. O app mostra todo relatório
 de despesas individuais e conjuntas, facilitando no fim do mês a divisão e o controle
 das despesas de casa.

# Status

:construction: Projeto parcialmente finalizado, ficamos felizes em receber sugestões de funcionalidades através do github :construction:

# Funcionalidades e Demonstração da Aplicação

- `Cadastrar contas fixas`: Cadastre contas de aluguel, água e condomínio para ter total controle das suas contas fixas. Marque incluso água e/ou condomínopara calculo automatico dos relativos valores a pagar, na tela de pagamento irá apresentar botões para pagamentos caso já pago os botões irão aparece inativos.
- `Cadastrar despesas`: Na tela de cadastrar despesas, você pode cadastrar pagamentos variados ou cadastrar valores devedores ao outro usuário no qual cadastrou para dividir as contas de casa.
- `Ver minhas despesas`: Nesta tela será apresentado um relatório de todas suas despesas pessoais ou despesas de casa que serão divididas com o outro usuário.
- `Relatórios`: Tela mostrará todo relatorio de despesas de ambos usuários, calculando a divisão de valores para cada ou valores que devem um ao outro.

https://user-images.githubusercontent.com/115194365/201999393-52029d4d-1e52-4ae7-9457-8446befdd439.mp4


# Tecnologias utilizadas

- `Python 3.9`
- `KivyMD`
- `Firebase`
- `API rest (Google)`
- `Paradigma de orientação a objetos`

# Desenvolvedor

| [<img src="https://user-images.githubusercontent.com/115194365/202005566-f6278b6c-4f75-416f-b01c-e79b8d04f02e.jpg" width=115><br><sub>Daniel de Souza Amorim</sub>](https://github.com/DaniellsamorimGit) |
| :---: | 


#### Mais sobre o autor: <br>
Graduado em Engenharia de computação em 2010 pela Universidade Potiguar do RN;<br>
Pós-graduado em Petróleo e gás;<br>
Desenvolvedor de dispositivos embarcados, microcontrolados, automação de sistemas;<br>
Desenvolvedor de placas de CI, prototipagem e desenvolvimento;<br>
Amante de tecnologias e desenvolvimento Python.<br>

# Considerações Finais

Até o fim deste projeto o Google estava mudando suas políticas de deploy de App's na Play Store, por este motivo o 
App Contas de casa não foi publicado na plataforma do Google. Mas o arquivo APK deste projeto foi gerado, em breve irei
disponibilizar aqui o APK para download, mas quem tiver curiosidade de como gerar um APK para publicação (versão debug) segue abaixo 
um breve tutorial (linux) de como fazer deploy de aplicativos (em breve passo a passo deploy versão release).

# Tutorial Deploy

OBS: Todo processo de deploy foi feito numa máquina virtual com Linux instalado, segue link para baixar a máquina virtual<br>
VIRTUAL BOX EM: https://virtualbox.br.uptodown.com/windows

- Preparando a máquina para deploy:<br>

### Tirar o modo hibernar do virtualbox
- Em settings -> power -> never

### Vamos instalar o GIT na maquina virtual (Abra o terminal do linux)

	sudo apt-get install git
Digite sua senha ubunto

### Caso de erro na instalação execute os passos abaixo e volte a instalar acima

	sudo rm -vf /var/lib/apt/lists/*
	sudo apt-get update
 
### Instalando o buildozer

	git clone https://github.com/kivy/buildozer.git
	sudo apt-get install python3.8
	sudo apt-get install -y python3-setuptools
 
### Instalando setup.py na pasta do buildozer

	cd buildoze
	sudo python3 setup.py install

* Saia da pasta do buildozer (cd)

### Instalar e atualizar todos os pacotes 
Se der erro reinicie sua máquina virtual

    sudo apt update
- Digite sua senha linux
 
### Agora vamos instalar vários pacotes necessários para deploy

    sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

### Vamos instalar nosso ambiente virtual

    pip3 install --user --upgrade cython virtualenv
    sudo apt-get install cython
    
* A partir daqui nossa maquina virtual esta pronta, "não" será necessário repetir os passos acima a cada novo deploy    

### Máquina pronta, vá no github pegar o link do projeto que irá fazer o deploy
* Na pasta raiz do terminal linux;
* Agora vamos baixar (git clone) ou atualizar (git pull) nosso projeto na pasta do linux;<br>

git clone https://github.com/DaniellsamorimGit/Appcontasdecasa.git<br>
git pull https://github.com/DaniellsamorimGit/Appcontasdecasa.git<br>

* Irá pedir usuario e senha do seu github
* A senha será o token gerado pelo proprio git
* para pegar o token va em github -> settings -> developer settings -> generate new token


### Entrar na pasta do app

* Agora na pasta do app:

      cd [nome do seu app] (ex: cd appcontasdecasa)

### Vamos criar o arquivo buildozer.spec

    buildozer init
    
### Buildozer configurações
* Abra o arquivo buldozer no bloco de notas e edite conforme abaixo:

	- 04 - title = [nome do seu app]
	- 07 - package.name: [mesmo nome acima so que minusculo e junto]
	- 10 - package.domain = [org.(nome do dominio, importante sem nome test)
	- 15 -  source files:
		-todas as extensoes dos arquivos usados no projeto (ex:txt)
	- 30 - versao do app: coloca a versao do deploy la do git
	- 39 - requirements = todas as bibliotecas usadas no app
		(pyton3,kivy,requests,certifi,urllib3,chardet,idna,pillow) 
		#requests sempre precisa de urllib3,chardet,idna
	- 88 ou 96 - descomenta pemissoes (INTERNET)
	- 216 ou 255 - descomentar: android.logcat (debug de erros)
	- 268 - arch : armeabl-v7a e arm64-v8a 

### Connecte o celular com o cabo e vamos fazer o deploy

* Habilite as opcoes de desenvolvedor no celular: marcar debug e sempre ativo
* Digite no terminal:

      buildozer android debug deploy run logcat

# :construction: PRONTO SE TUDO DER CERTO O APK IRA APARECER NA PASTA INIT E INSTALADO NO SEU SMARTPHONE :construction:

### Obs: É comum no meio do processo surgirem erros, mas não desanime, abaixo listei algumas soluções para erros mais comuns:


#### ERRO COM JAVA TENTE:<br>

    sudo add-apt-repository ppa:linuxuprising/java 
    sudo apt install oracle-java17-installer --install-recommends

#### ERRO COM KIVY TENTE:<br>
    sudo apt-get install python3-pip
    sudo apt-get purge python3-kivy

##### depois veja a versão do python:
    python3 -V

##### acesse a pagina:
https://kivy.org/downloads/ci/linux/kivy/

##### na página copie o link referente a sua versão do python
(Se seu PC for intel escolha X86_64, e para AMD escolha AARCH64)
RODE O COMANDO ABAIXO JUNTO COM O LINK COPIADO:

    python3 -m pip install https://kivy.org/downloads/ci/linux/kivy/Kivy-2.2.0.dev0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl --user

#### ERRO COM PIL TENTE:
adicione "pillow" nos requerimentos do buildozer na linha 39

obs: PIL faz parte da biblioteca pillow, eu coloco em todos apps por padrão.


#### ERRO PYTHON3 OU PYTHON3 NÃO ATENTE OS REQUERIMENTOS:
apague "python3" da lista de requerimentos do buildozzer


#### ERRO GRADLE TENTE:
    sudo apt-get install openjdk-11-jdk

obs: atualiza o jdk de 8 para 11

#### USA O KIVYMD? INSTALE TODO O PACOTE:
    pip install --force-reinstall https://github.com/kivymd/KivyMD/archive/master.zip

Vai instalar: 
Successfully installed Kivy-Garden-0.1.5 certifi-2022.9.24 charset-normalizer-2.1.1 docutils-0.19 idna-3.4 kivy-2.1.0 kivymd-1.1.0.dev0 pillow-9.2.0 pygments-2.13.0 requests-2.28.1 urllib3-1.26.12


#### DICA:
o aplicativo foi instalado no celular mas não abre?
instale o pacote abaixo para ver o DEBUG, e erros que estão ocorrendo:

    sudo apt install adb

depois de instalado o ADB, conecte o celular e rode:

    adb logcat -s python

O erro será apresentado na tela (caso exista) assim como no RUN do pycharm

### SUCESSO!!!






