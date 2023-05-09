from PIL import Image, ImageDraw, ImageFont
from random import randint


# Функция генерирует карточки
def create_image(name):
    img = Image.new('RGB', (850, 500), 'white')
    font = ImageFont.truetype('data/lato-light.ttf', size=50)
    idraw = ImageDraw.Draw(img)
    i1 = randint(1, 15)
    i2 = randint(1, 15) * 1024
    i3 = randint(1, 15) * 2 ** 13
    i4 = randint(1, 15)
    i5 = randint(1, 15)
    ans1 = f'{i1 * 2 ** 10},{i1 * 2 ** 13}'
    ans2 = f'{i2 // 2 ** 10},{i2 * 8}'
    ans3 = f'{i3 // 2 ** 13},{i3 // 8}'
    ans4 = f'{i4 * 2 ** 23}'
    ans5 = f'{i5 * 2 ** 20},{i5 * 2 ** 27}'
    a = [f'{i1} Кбайт = ? байта = ? бит',
         f'? Кбайт = {i2} байта = ? бит',
         f'? Кбайт = ? байта = {i3} бит',
         f'{i4} Мбайт = ? бит',
         f'{i5} Гбит = ? Кбит = ? байт']
    for i in range(1, 6):
        idraw.text((30, 50 + 75 * (i - 1)), f"""{i}) {a[i - 1]}""", font=font, fill=(0, 0, 0))
    img.save(f'data/card{name}.jpg')
    return f"{ans1},{ans2},{ans3},{ans4},{ans5}"

# img = Image.open('data/card.jpg')
# img.show()
# print(ans1, ans2, ans3, ans4, ans5)
