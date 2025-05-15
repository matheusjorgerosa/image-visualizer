import FreeSimpleGUI as sg
import cv2
import numpy as np

class img_manipulation:
    def __init__(self):
        self.original_img = None
        self.current_img = None
        self.history = []

        # Left column with controls (sidebar) - removed rotation, flip, and rescale controls
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
            [sg.Button('Nitidez', key='-SHARP-')],
            [sg.Button('Bordas', key='-EDGE-')],
            [sg.Button('Desfoque', key='-BLUR-')]
        ]

        # Right column for displaying images
        image_column = [
            [sg.Image(key='-ORIGINAL-')],
            [sg.Image(key='-PROCESSED-')]
        ]

        layout = [
            [
                sg.Column(left_column, vertical_alignment='top'),
                sg.VSeperator(),
                sg.Column(image_column, expand_x=True, expand_y=True)
            ]
        ]
        self.window = sg.Window('Visualizador', layout, resizable=True, finalize=True, size=(800, 600))

    def update_display(self):
        if self.original_img is None or self.current_img is None:
            return

        height = 300
        def resize_img(img):
            ratio = height / img.shape[0]
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

    def add_history(self, img):
        self.current_img = img
        self.history.append(img.copy())
        self.update_display()

    def run(self):
        while True:
            event, values = self.window.read(timeout=100)
            if event in (sg.WIN_CLOSED, 'Cancelar'):
                break

            if event == '-LOAD-':
                file_path = sg.popup_get_file(
                    'Selecione',
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
                        sg.popup_error('Arquivo inválidoo!')
                    else:
                        self.original_img = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
                        self.current_img = self.original_img.copy()
                        self.history = [self.original_img.copy()]
                        self.update_display()

            elif event == '-SAVE-':
                if self.current_img is not None:
                    save_path = sg.popup_get_file('Salvar como', save_as=True, default_extension='.png', 
                                                  file_types=(('PNG', '*.png'),))
                    if save_path:
                        try:
                            cv2.imwrite(save_path, cv2.cvtColor(self.current_img, cv2.COLOR_RGB2BGR))
                        except Exception as err:
                            sg.popup_error('Erro ao salvar imagem: ' + str(err))

            elif event == '-UNDO-':
                if len(self.history) > 1:
                    self.history.pop()
                    self.current_img = self.history[-1].copy()
                    self.update_display()

            elif event == '-CLEAR-':
                if self.original_img is not None:
                    self.current_img = self.original_img.copy()
                    self.history = [self.original_img.copy()]
                    self.update_display()

            elif event == '-GRAY-':
                if self.current_img is not None:
                    gray = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2GRAY)
                    gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
                    self.add_history(gray_rgb)

            elif event == '-INV-':
                if self.current_img is not None:
                    inverted = 255 - self.current_img
                    self.add_history(inverted)

            elif event == '-CONTRAST-':
                if self.current_img is not None:
                    lab = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    cl = clahe.apply(l)
                    merged = cv2.merge((cl, a, b))
                    contrast_img = cv2.cvtColor(merged, cv2.COLOR_LAB2RGB)
                    self.add_history(contrast_img)

            elif event == '-SHARP-':
                if self.current_img is not None:
                    kernel = np.array([[-1, -1, -1],
                                       [-1, 9, -1],
                                       [-1, -1, -1]])
                    sharp_img = cv2.filter2D(self.current_img, -1, kernel)
                    self.add_history(sharp_img)

            elif event == '-EDGE-':
                if self.current_img is not None:
                    gray = cv2.cvtColor(self.current_img, cv2.COLOR_RGB2GRAY)
                    edges = cv2.Canny(gray, 100, 200)
                    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
                    self.add_history(edges_rgb)

            elif event == '-BLUR-':
                if self.current_img is not None:
                    blurred = cv2.GaussianBlur(self.current_img, (11, 11), 0)
                    self.add_history(blurred)

        self.window.close()

if __name__ == '__main__':
    iv = img_manipulation()
    iv.run()
