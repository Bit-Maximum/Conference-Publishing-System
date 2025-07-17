import docx2txt
import glob

from PIL import Image, ImageOps

import os
import shutil

from lxml import etree


def paragraph_contains_image(p) -> bool:
    return any("pic:pic" in run.element.xml for run in p.runs)


def paragraph_contains_formula(p) -> bool:
    xml_str = p._element.xml
    tree = etree.fromstring(xml_str.encode())

    for elem in tree.iter():
        if elem.tag.endswith('oMath'):
            return True


def paragraph_contains_numbering(p):
    numbering_properties = p._element.xpath('.//w:numPr')
    return len(numbering_properties) > 0 or str(p.style).split("'")[1] == 'List Bullet' or str(p.style).split("'")[1] == 'List Number'


def collect_images(document_path, output_dir_path, user_id):
    out_path = os.path.join(output_dir_path, str(user_id))
    os.makedirs(out_path)
    docx2txt.process(document_path, out_path)
    imgs = []
    for file in glob.glob(os.path.join(out_path, "*.*")):
        imgs.append(file)
    return imgs


def remove_images_directory(img_dir_path, session_id):
    try:
        dir = os.path.join(img_dir_path, str(session_id))
        shutil.rmtree(dir)
        return True
    except Exception as e:
        print(e)
        return False


def get_shapes(document):
    return [s for s in document.inline_shapes]


def get_images_shapes(document):
    shapes = [s for s in document.inline_shapes]
    blob_shapes = []
    for inline_shape in shapes:
        blip = inline_shape._inline.graphic.graphicData.pic.blipFill.blip
        rId = blip.embed
        document_part = document.part
        image_part = document_part.related_parts[rId]
        image = image_part._blob
        blob_shapes.append(image)


def add_border(input_image, output_image, border):
    img = Image.open(input_image)
    if isinstance(border, int) or isinstance(border, tuple):
        bimg = ImageOps.expand(img, border=border, fill=(0, 0, 0))
    else:
        raise RuntimeError('Border is not an image or tuple')
    bimg.save(output_image)
