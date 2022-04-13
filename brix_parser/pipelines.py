# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import fpdf
import qrcode
import os
from datetime import datetime
from collections import OrderedDict

from paths import *


fpdf.set_global("SYSTEM_TTFONTS", os.path.join(os.path.dirname(__file__),'fonts'))


def print_characteristics_line(pdf, characteristics, start_y):
    start_x = 85
    char_name_y = start_y
    for char in characteristics:
        pdf.set_font('DejaVu', '', 7)
        pdf.text(x=start_x, y=char_name_y, txt=char[0])
        pdf.set_font('DejaVuBold', '', 14)

        curr_text = char[1]
        result_text = []
        words = curr_text.split(" ")

        j = 0
        for i, text in enumerate(words):
            if len(words) == 1:
                if len(text) >= 13:
                    result_text.append(text[0:9] + "...")
                else:
                    result_text.append(text)
                break
            if i == 0:
                result_text.append(text + " ")
                j += 1
                continue
            if len(result_text[j - 1]) >= 7:
                result_text.append(text + " ")
                j += 1
            elif len(text) + len(result_text[j - 1]) >= 13:
                result_text.append(text + " ")
                j += 1
            else:
                result_text[j - 1] += text

        value_y = start_y + 6
        for text in result_text:
            pdf.text(x=start_x, y=value_y, txt=text)
            value_y += 5

        start_x += 38


def get_with_break(input_str, chars_count):
    result = []
    if len(input_str) > chars_count:
        result.append(input_str[0:chars_count])
        if len(input_str[chars_count:]) > chars_count:
            result.append(input_str[chars_count:chars_count * 2 - 3] + "...")
        else:
            result.append(input_str[chars_count:])
    else:
        result.append(input_str)

    return result


def make_pdf(article, url, characteristics, compatibles, oem, output_path, source_img_path, id_):
    pdf = fpdf.FPDF(orientation='L', unit='mm', format=(100, 200))
    pdf.add_font('DejaVuBold', '', 'DejaVuSansCondensed-Bold.ttf', uni=True)
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVuBold', '', 30)
    pdf.add_page()
    pdf.image(source_img_path, x=0, y=0, w=200, h=100, type='', link='')

    pdf.set_x(1000)

    pdf.text(x=8, y=17, txt=article)

    pdf.set_font('DejaVu', '', 7)

    start_y = 28
    for compatible in compatibles:
        name = get_with_break(compatible[0], 18)
        for i, n in enumerate(name):
            pdf.text(x=9, y=start_y + 2.5 * i, txt=n)

        model = get_with_break(compatible[1], 12)
        for i, m in enumerate(model):
            pdf.text(x=37, y=start_y + 2.5 * i, txt=m)

        pdf.text(x=57, y=start_y, txt=compatible[2])

        if len(name) == 2 or len(model) == 2:
            start_y += 2

        start_y += 4.5

        if start_y >= 60:
            break

    new_chars = OrderedDict({"Сторона установки": "", "Количество дисков": "", "Тип тормозного диска": "",
                            "Наружный диаметр ": "", "Диаметр центрирования ": "", "Диаметр центрирования [мм]": "",
                             "Высота ": "", "Высота [мм]": ""})
    for k, v in characteristics.items():
        new_chars.update({k: v})
        #if new_chars.get(k, False):
        #    new_chars.update({k: v})

    i = 0
    while i != len(list(new_chars.items())):
        items = list(new_chars.items())
        if items[i][1] == "":
            new_chars.pop(items[i][0])
        else:
            i += 1

    print(new_chars)
    #characteristics_list = list(characteristics.items())
    characteristics_list = list(new_chars.items())

    print_characteristics_line(pdf, characteristics_list[0:3], 28)
    print_characteristics_line(pdf, characteristics_list[3:6], 48)

    pdf.set_font('DejaVu', '', 7)
    pdf.text(x=84, y=14, txt="   ".join(oem))

    qrcode_name = os.path.join(TMP_PATH, f"{article}_{id_}.png")
    img = qrcode.make(url)
    img.save(qrcode_name)

    pdf.image(qrcode_name, x=117, y=75, w=15)

    pdf.output(output_path)
    os.remove(qrcode_name)


class BrixParserPipeline:
    def __init__(self):
        self.result_path = os.path.join(
            RESULTS_PATH,
            str(datetime.now()).replace(" ", "_").split(".")[0].replace(":", "-")
        )
        os.mkdir(self.result_path)

    def process_item(self, item, spider):
        output_path = os.path.join(self.result_path, f"{item['article']}.pdf")
        source_img_path = os.path.join(THIS_PATH, "pdf.jpg")
        make_pdf(article=item["article"], url=item["url"], characteristics=item["characteristics"], oem=item["oem"],
                 compatibles=item["compatibles"][0:8], output_path=output_path, source_img_path=source_img_path,
                 id_=item["id"])

        return item
