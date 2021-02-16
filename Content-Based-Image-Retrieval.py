from PIL import Image
import numpy as np
import os
import random
import math


def rgb_to_hsv(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360

    return h


# hue degerine gore yapilan benzerlik testinde kullanilan histogram hesaplama fonksiyonu
def histogram_h(im):

    height, width = im.size
    count = 0
    histogram = np.zeros(360)  # 0'larla dolu dizi olustur

    for x in range(0, height):
        for y in range(0, width):
            r, g, b = im.getpixel((x, y))  # hue degerini al
            h = rgb_to_hsv(r, g, b)
            histogram[int(h)] += 1  # histogram dizisi olustur

    # normalizasyon
    for i in range(0, 360):
        count += histogram[i]
    for i in range(0, 360):
        histogram[i] /= count   # histogramdaki her degeri toplam pixel sayisina bol

    return histogram


# RGB uzayina gore yapilan benzerlik testinde kullanilan histogram hesaplama fonksiyonu
def histogram_rgb(im):

    height, width = im.size
    count_r = 0
    count_g = 0
    count_b = 0
    HistogramR = np.zeros(256)  # 0'larla dolu dizi olustur
    HistogramG = np.zeros(256)
    HistogramB = np.zeros(256)

    for x in range(0, height):
        for y in range(0, width):
            r, g, b = im.getpixel((x, y))  # r, g, b degerlerini al
            HistogramR[r] += 1  # histogram dizisi olustur
            HistogramG[g] += 1
            HistogramB[b] += 1

    # normalizasyon
    for i in range(0, 256):
        count_r += HistogramR[i]
        count_g += HistogramG[i]
        count_b += HistogramB[i]
    for i in range(0, 256):         # histogramdaki her degeri toplam pixel sayisina bol
        HistogramR[i] /= count_r
        HistogramG[i] /= count_g
        HistogramB[i] /= count_b

    return HistogramR, HistogramG, HistogramB


# Verilen listede verilen image isminin olup olmadigina bak
def search(list, name):
    for i in range(len(list)):
        if list[i] == name:
            return False
    return True


# rgb'de  histogramlar arasinda distance hesapla
def calc_distance_rgb(histogramr1, histogramr2, histogramg1, histogramg2, histogramb1, histogramb2):

    distance = 0
    for x in range(0, 256):
        rd = histogramr1[x] - histogramr2[x]
        gd = histogramg1[x] - histogramg2[x]
        bd = histogramb1[x] - histogramb2[x]
        distance += math.sqrt(rd * rd + gd * gd + bd * bd)

    return distance


# hue degeri icin  histogramlar arasinda distance hesapla
def calc_distance_h(histogramh1, histogramh2):
    distance = 0
    for x in range(0, 360):
        d = histogramh1[x] - histogramh2[x]
        distance += math.sqrt(d * d)

    return distance


# dosyadan random image alip, verilen flag degerine gore test veya train icin listeye kaydet
def take_images(tests, images, path, i, flag):
    count = 0
    while count < i:
        random_filename = random.choice([
            x for x in os.listdir(path)
            if os.path.isfile(os.path.join(path, x)) and x.endswith('.jpg')
        ])
        if flag == 0:
            if search(tests, random_filename):
                count += 1
                tests.append(random_filename)  # tests'e her classten 5 tane (6*5) test resmi kaydet
        if flag == 1:
            if search(tests, random_filename) and search(images, random_filename):
                count += 1
                images.append(random_filename)  # images e her siniftan 25 tane egitim resimlerini kaydet
    if flag == 0:
        return tests
    else:
        return images


# distances 'da tutulan distance'lar arasindaki en kucuk 5 tanesini bul
def find_similar_images(distances, images):
    for x in range(0, 5):
        i = distances.index(min(distances))
        image = Image.open(images[i])
        print(images[i])
        distances.remove(min(distances))
    distances.clear()


def rgb(tests, images, rgb_histograms):
    print("------------------------------")
    print("-------------RGB--------------")
    print("------------------------------")
    # 30 test resmiyle r, g, b ye gore benzerlik testi yap
    for count in range(0, 30):
        distances = []  #
        image1 = Image.open(tests[count]).convert('RGB')
        print([count+1], ".Test Resmi: ", tests[count])
        histogramr1, histogramg1, histogramb1 = histogram_rgb(image1)

        # daha onceden kaydedilen 150 tane resmin rgb histogramlariyla islem yap
        j = 0
        while j < 450:
            histogramr2 = rgb_histograms[j]
            j += 1
            histogramg2 = rgb_histograms[j]
            j += 1
            histogramb2 = rgb_histograms[j]
            distance = calc_distance_rgb(histogramr1, histogramr2, histogramg1, histogramg2, histogramb1, histogramb2)
            distances.append(distance)  # distance'ları diziye kaydet
            j += 1

        # en yakin 5 resmi bul
        find_similar_images(distances, images)


def hue(tests, images, h_histograms):
    print("------------------------------")
    print("-------------HUE--------------")
    print("------------------------------")
    # HUE
    # 30 test resmiyle hue ya gore benzerlik testi yap
    for count in range(0, 30):
        distances = []
        image1 = Image.open(tests[count]).convert('RGB')
        print([count+1], ". Test Resmi: ", tests[count])
        histogramh1 = histogram_h(image1)

        j = 0
        while j < 150:
            histogramh2 = h_histograms[j]
            distance = calc_distance_h(histogramh1, histogramh2)
            distances.append(distance)  # distance'ları diziye kaydet
            j += 1

        # en yakin 5 resmi bul
        find_similar_images(distances, images)


# rgb ve h icin histogramlari hesapla ve ilgili listeye kaydet
def save_histograms(images, rgb_histograms, h_histograms):

    # 150 resim icin r, g, b ,h histogramlarini diziye kaydet
    for i in range(0, 150):
        image2 = Image.open(images[i]).convert('RGB')   # images listesindeki train image'lerini ac
        histogramr2, histogramg2, histogramb2 = histogram_rgb(image2)  # rgb histogramlarini hesapla

        # hesaplanan histogramlari rgb_histograms listesine sirayla kaydet
        rgb_histograms.append(histogramr2)
        rgb_histograms.append(histogramg2)
        rgb_histograms.append(histogramb2)

        histogramh = histogram_h(image2)  # hue icin histogram hesapla
        # hesaplanan hue histogramini h_histograms listesine kaydet
        h_histograms.append(histogramh)

    return rgb_histograms, h_histograms


def take_random_images(tests, images):
    # test ve egitim resimlerini her bir class'tan take_images() ile random secerek test veya images listesine kaydet
    # Her class'tan 5 test, 25 eğitim resmi al
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/028.camel"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/056.dog"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/057.dolphin"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/084.giraffe"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/089.goose"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    path = "/Users/hilaldogan/Desktop/GoruntuOdev2/105.horse"
    tests = take_images(tests, images, path, 5, 0)
    images = take_images(tests, images, path, 25, 1)
    return tests, images


def main():

    tests = []  # test imagelerinin oldugu liste
    images = []  # train imagelerinin oldugu liste
    rgb_histograms = []  # rgb histogramlarinin tutuldugu liste
    h_histograms = []   # hue histogramlarinin tutuldugu liste

    tests, images = take_random_images(tests, images)  # test ve train image'lerini random olarak sec

    # rgb ve h icin histogramlari hesapla ve ilgili listeye kaydet
    rgb_histograms, h_histograms = save_histograms(images, rgb_histograms, h_histograms)

    rgb(tests, images, rgb_histograms)   # RGB icin distance'i en az olan 5 resmi bul
    hue(tests, images, h_histograms)    # Hue icin distance'i en az olan 5 resmi bul


if __name__ == "__main__":
    main()
