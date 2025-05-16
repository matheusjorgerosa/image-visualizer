# Atividade Ponderada - Semana 3

&emsp; O seguinte repositório visa atender às expectativas e demandas da Atividade Ponderada da Semana 3. Abaixo, listam-se as funcionalidades do programa desenvolvido e método de execução.

## Funcionalidades

&emsp; Conforme sugerido no comando da Atividade Ponderada, neste projeto aplicam-se os filtros: escala de cinza, inversão de cores, aumento de contraste, desfoque (blur), nitidez (sharpen), detecção de bordas.

- Escala de Cinza: Converte a imagem colorida importada pelo usuário em tons de cinza.

- Inversão de Cores: Inverte o valor numérico de cor de cada píxel pelo seu oposto.

- Aumento de Contraste: Realça as diferenças entre regiões claras e escuras da imagem, melhorando a distinção de detalhes.

- Desfoque: Aplica-se cálculo matricial para suavizar a imagem, reduzindo detalhes e ruídos.

- Nitidez: Aumenta o contraste em contornos através de um cálculo matricial, enfatizando transições.

- Detecção de Bordas: Com a aplicação de diversos filtros, identifica variações bruscas de intensidade (bordas), e as realça.

## Modo de Execução

### 1º Passo

&emsp; Dentro do diretório da Atividade Ponderada, execute os comandos:

```bash
python -m venv venv

source venv/bin/activate

pip install -r requirements.txt
```

### 2º Passo

&emsp; Execute o arquivo `image_visualizer.py`.

### 3º Passo

&emsp; Importe uma imagem no programa aberto e explore os filtros!

## Demonstração

&emsp; Acesse o vídeo de demonstração do projeto clicando [aqui](https://drive.google.com/file/d/14xhbXArr4oRB99qQTxwymQU4f4dTewQ1/view?usp=sharing)!