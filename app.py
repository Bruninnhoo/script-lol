import customtkinter as ctk
from PIL import Image
import requests
import threading
import pyautogui
import time


# Variável global para controle da execução
running = False
ctk.set_appearance_mode("dark")  # Tema escuro
ctk.set_default_color_theme("blue")  # Tema azul


control = pyautogui


def check_screen(string):
    try:
        target = control.locateOnScreen(f'img/{string}.png', confidence=0.8)

        if string == 'lobby' or string == 'ban':
            return True

        if target != None:
            return (target.left, target.top)

    except pyautogui.ImageNotFoundException:
        print('...')
        time.sleep(2)


def click(x, y):
    control.click(x, y)


def accept_match():
    locale = check_screen('accept')

    if locale != None:
        click(locale[0], locale[1])
        time.sleep(10)


def champiom_select():
    if check_screen('lobby'):
        return True


def select_ban_champion(ban):
    try:
        verify = check_screen('ban_fase')

        if verify != None:
            search = check_screen('searchbar')

            if search != None:
                click(search[0], search[1])
                control.write(ban)

                reference = check_screen('reference')
                click(reference[0] + 10, reference[1] + 10)

                ban_button = check_screen('ban_button')

                if ban_button != None:
                    click(ban_button[0], ban_button[1])

    except pyautogui.ImageNotFoundException:
        print('...')
        time.sleep(2)

def select_champion(champion):
    try:
        verify = check_screen('select_fase')

        if verify != None:
            search = check_screen('searchbar')

            if search != None:
                click(search[0], search[1])
                control.write(champion)

                reference = check_screen('reference')
                click(reference[0] + 10, reference[1] + 10)

                accept_button = check_screen('ban_button')

                if accept_button != None:
                    click(accept_button[0], accept_button[1])

    except pyautogui.ImageNotFoundException:
        print('...')
        time.sleep(2)


def main_logic(ban, pick):
    try:
        while running:  
            accept_match()

            if champiom_select():
                while running: 
                    select_ban_champion(ban)
                    select_champion(pick)
                    if accept_match():
                        break
   
    except Exception as e:
        print(f"Erro durante o processo: {e}")


# Interface gráfica
def create_interface(champions):
    def update_status(message):
        """Atualiza o status na interface."""
        status_var.set(message)


    def filter_champions():
        """Filtra os campeões com base no texto da barra de pesquisa."""
        search_text = search_var.get().lower()
        for widget in icon_frame.winfo_children():
            widget.destroy()

        filtered_champions = {
            champ: data
            for champ, data in champions.items()
            if search_text in champ.lower()
        }
        populate_icons(filtered_champions)

    def stop_process():
        """Função para parar o processo principal."""        
        global running
        running = False
        update_status("Processo parado.")
        

    def reset_selection():
        """Reseta as seleções de ban e pick e para o processo em execução."""        
        global running
        stop_process()  
        ban_var.set("")
        pick_var.set("")
        search_var.set("")
        populate_icons(champions)
        update_status("Seleções resetadas.")

    def start_process():
        """Inicia o processo de aceitar partida, banir e selecionar campeão."""        
        global running
        if running:
            ctk.CTkMessageBox.show_info("Info", "O processo já está rodando!")
            return

        champion_ban = ban_var.get()
        champion_pick = pick_var.get()

        if not champion_ban or not champion_pick:
            ctk.CTkMessageBox.show_error("Erro", "Selecione um campeão para banir e um para jogar!")
            return

        running = True  
        threading.Thread(target=main_logic, args=(champion_ban, champion_pick), daemon=True).start()
        update_status("Processo iniciado...")

    def populate_icons(champions_to_display):
        """Exibe os ícones dos campeões no frame."""        
        row, col = 0, 0
        for champ, data in champions_to_display.items():
            image_url = f"http://ddragon.leagueoflegends.com/cdn/15.1.1/img/champion/{data['image']['full']}"
            response = requests.get(image_url, stream=True)
            img_data = Image.open(response.raw).resize((64, 64))
            img = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(64, 64))

            btn = ctk.CTkButton(
                icon_frame,
                image=img,
                text=champ,
                compound="top",
                command=lambda champ=champ: on_champion_click(champ),
                fg_color="gray30",
                hover_color="gray50",
                text_color="white",
                width=80,
                height=100,
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col >= 10:
                col = 0
                row += 1

    def on_champion_click(champion_name):
        """Gerencia cliques nos botões dos campeões."""        
        if not ban_var.get():
            ban_var.set(champion_name)
        elif not pick_var.get():
            pick_var.set(champion_name)
        else:
            ctk.CTkMessageBox.show_info("Info", "Você já selecionou o ban e o pick!")

    # Janela principal
    root = ctk.CTk()
    root.title("Seleção de Campeões")
    root.geometry("1000x1100")

    # Frames principais
    top_frame = ctk.CTkFrame(root)
    top_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")

    middle_frame = ctk.CTkFrame(root)
    middle_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

    global icon_frame
    icon_frame = ctk.CTkScrollableFrame(root, width=950, height=500)
    icon_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")

    # Criação da aba de status
    tabview = ctk.CTkTabview(root)
    tabview.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

    tabview.add("Status")
    status_frame = ctk.CTkFrame(tabview)
    status_frame.grid(padx=10, pady=10, sticky="ew")

    global status_var
    status_var = ctk.StringVar()
    status_var.set("Status: Pronto para iniciar.")  # Status inicial

    status_label = ctk.CTkLabel(status_frame, textvariable=status_var, anchor="w")
    status_label.grid(sticky="ew", padx=10, pady=5)

    # Labels e campos de entrada para ban e pick
    ctk.CTkLabel(top_frame, text="Campeão para banir:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    ban_var = ctk.StringVar()
    ctk.CTkEntry(top_frame, textvariable=ban_var, state="readonly").grid(row=0, column=1, padx=10, pady=5)

    ctk.CTkLabel(top_frame, text="Campeão para jogar:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    pick_var = ctk.StringVar()
    ctk.CTkEntry(top_frame, textvariable=pick_var, state="readonly").grid(row=1, column=1, padx=10, pady=5)

    # Barra de pesquisa
    search_var = ctk.StringVar()
    ctk.CTkEntry(middle_frame, textvariable=search_var, placeholder_text="Pesquise um campeão...").grid(row=0, column=0, padx=5)
    ctk.CTkButton(middle_frame, text="Buscar", command=filter_champions).grid(row=0, column=1, padx=5)

    # Botões de reset e start
    ctk.CTkButton(middle_frame, text="Reset", command=reset_selection, fg_color="red").grid(row=0, column=2, padx=5)
    ctk.CTkButton(middle_frame, text="Start", command=start_process, fg_color="green").grid(row=0, column=3, padx=5)

    # Popula os ícones inicialmente
    populate_icons(champions)

    root.mainloop()


# Função para iniciar a aplicação
def main():
    url = 'https://ddragon.leagueoflegends.com/cdn/15.1.1/data/en_US/champion.json'

    try:
        response = requests.get(url)
        response.raise_for_status()
        champions = response.json()["data"]

        # Criar a interface gráfica
        create_interface(champions)

    except requests.RequestException as e:
        print(f"Erro ao acessar o JSON: {e}")
    except KeyError as e:
        print(f"Erro ao acessar os dados dos campeões: {e}")


if __name__ == "__main__":
    main()


