import FreeSimpleGUI as sg
import cv2
import numpy as np

class img_manipulation:
    def __init__(self):
        self.original_img = None
        self.current_img = None
        self.history = []

        # Adiciona os botões de ações e filtros na coluna esquerda do canva da aplicação
        # Cada botão possui uma 'key' para identificação e futura lógica de eventos
        
        left_column = [
            [sg.Text('Ações:')],
            [sg.Button('Carregar', key='-LOAD-')],
            [sg.Button('Salvar', key='-SAVE-')],
            [sg.Button('Desfazer', key='-UNDO-')],
            [sg.Button('Limpar', key='-CLEAR-')],
            [sg.Text('Filtros/Transformações:')],
            [sg.Button('Cinza', key='-GRAY-')],
            [sg.Button('Inverter Cores', key='-INV-')],
            [sg.Button('Contraste', key='-CONTRAST-')],
            [sg.Button('Desfoque', key='-BLUR-')],
            [sg.Button('Nitidez', key='-SHARP-')],
            [sg.Button('Bordas', key='-EDGE-')],
        ]

        # Define a região à direita do canva da aplicação para exibir as imagens em lista
        image_column = [
            [sg.Text('Imagem Original:')],
            [sg.Image(key='-ORIGINAL-')],
            [sg.Text('Imagem Processada:')],
            [sg.Image(key='-PROCESSED-')]
        ]

        # Define o layout da aplicação, com alinhamento superior para a sidebar de ações e filtros
        layout = [
            [
                sg.Column(left_column, vertical_alignment='top'),
                sg.VSeperator(),
                sg.Column(image_column, expand_x=True, expand_y=True)
            ]
        ]
        self.window = sg.Window('Image Visualizer', layout, resizable=True, finalize=True, size=(800, 600))

    def update_display(self):
        if self.original_img is None or self.current_img is None:
            return

        height = 300

        # Função para redimensionar a imagem ao canva mantendo sua proporção original
        def resize_img(img):
            ratio = height / img.shape[0] # Identificação da proporção (altura da imagem / altura do canva)
            new_width = int(img.shape[1] * ratio)
            return cv2.resize(img, (new_width, height))

        orig_resized = resize_img(self.original_img)
        curr_resized = resize_img(self.current_img)

        if len(orig_resized.shape) == 3 and orig_resized.shape[2] == 3:
            if np.mean(orig_resized[:, :, 0]) > np.mean(orig_resized[:, :, 2]):
                orig_resized = cv2.cvtColor(orig_resized, cv2.COLOR_BGR2RGB)
        if len(curr_resized.shape) == 3 and curr_resized.shape[2] == 3:
            if np.mean(curr_resized[:, :, 0]) > np.mean(curr_resized[:, :, 2]):
                curr_resized = cv2.cvtColor(curr_resized, cv2.COLOR_BGR2RGB)

        ret1, buf1 = cv2.imencode('.png', orig_resized)
        ret2, buf2 = cv2.imencode('.png', curr_resized)
        data1 = buf1.tobytes() if ret1 else None
        data2 = buf2.tobytes() if ret2 else None

        self.window['-ORIGINAL-'].update(data=data1)
        self.window['-PROCESSED-'].update(data=data2)

    # Função para adicionar a imagem atual à lista de histórico e permitir ação de 'undo'
    def add_history(self, img):
        self.current_img = img
        self.history.append(img.copy())
        self.update_display()

    def run(self):
        # Loop principal da aplicação
        while True:
            event, values = self.window.read(timeout=100)
            if event in (sg.WIN_CLOSED, 'Cancelar'):
                break

            # Lógicas de cada botão da sidebar

            # Clique no botão de 'Carregar' permite busca de imagem no computador e filtra imagens por extensão
            if event == '-LOAD-':
                file_path = sg.popup_get_file(
                    'Selecione',
                    # Filtro de arquivos por extensão
                    file_types=(
                        ('PNG Files', '*.png'),
                        ('JPEG Files', '*.jpg;*.jpeg'),
                        ('Bitmap Files', '*.bmp'),
                        ('GIF Files', '*.gif'),
                    )
                )
                if file_path:
                    temp = cv2.imread(file_path)
                    if temp is None:
                        sg.popup_error('Arquivo inválido ou formato não suportado')
                    else:
                        self.original_img = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
                        self.current_img = self.original_img.copy()
                        self.history = [self.original_img.copy()]
                        self.update_display()

            # Clique no botão de 'Salvar' permite salvar a imagem processada
            elif event == '-SAVE-':
                if self.current_img is not None:
                    save_path = sg.popup_get_file('Salvar como', save_as=True, default_extension='.png', 
                                                  file_types=(('PNG', '*.png'),))
                    if save_path:
                        try:
                            cv2.imwrite(save_path, cv2.cvtColor(self.current_img, cv2.COLOR_RGB2BGR))
                        except Exception as err:
                            sg.popup_error('Erro ao salvar imagem: ' + str(err))

            # Clique no botão de 'Desfazer' permite desfazer a última ação
            elif event == '-UNDO-':
                if len(self.history) > 1:
                    self.history.pop()
                    self.current_img = self.history[-1].copy()
                    self.update_display()

            # Clique no botão de 'Limpar' permite limpar a imagem atual e voltar para a original
            elif event == '-CLEAR-':
                if self.original_img is not None:
                    self.current_img = self.original_img.copy()
                    self.history = [self.original_img.copy()]
                    self.update_display()

            # Clique no botão de 'Cinza' converte a imagem atual para escala de cinza
            elif event == '-GRAY-':
                if self.current_img is not None:
                    gray = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2GRAY)
                    gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                    self.add_history(gray_rgb)

            # Clique no botão de 'Inverter Cores' inverte as cores da imagem atual
            elif event == '-INV-':
                if self.current_img is not None:
                    inverted = 255 - self.current_img
                    self.add_history(inverted)

            # Clique no botão de 'Contraste' aplica o filtro CLAHE para aumentar o contraste da imagem atual
            elif event == '-CONTRAST-':
                if self.current_img is not None:
                    lab = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    cl = clahe.apply(l)
                    merged = cv2.merge((cl, a, b))
                    contrast_img = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
                    self.add_history(contrast_img)

            # Clique no botão de 'Nitidez' aplica o filtro de nitidez na imagem atual
            elif event == '-SHARP-':
                if self.current_img is not None:
                    # Matriz de convolução para o filtro de nitidez a ser aplicado na imagem
                    kernel = np.array([[-1, -1, -1],
                                       [-1, 9, -1],
                                       [-1, -1, -1]])
                    sharp_img = cv2.filter2D(self.current_img, -1, kernel)
                    self.add_history(sharp_img)

            # Clique no botão de 'Bordas' aplica o filtro de detecção de bordas na imagem atual
            elif event == '-EDGE-':
                if self.current_img is not None:
                    gray = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2GRAY)
                    edges = cv2.Canny(gray, 100, 200)
                    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                    self.add_history(edges_rgb)

            # Clique no botão de 'Desfoque' aplica o filtro de desfoque na imagem atual
            elif event == '-BLUR-':
                if self.current_img is not None:
                    blurred = cv2.GaussianBlur(self.current_img, (11, 11), 0)
                    self.add_history(blurred)

        self.window.close()

if __name__ == '__main__':
    iv = img_manipulation()
    iv.run()
