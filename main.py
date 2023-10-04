import numpy as np
import cv2

class Szachy:
	def __init__(self):
		self.współrzędne = { 'x9': [1000000,1000000]}   # dziennik współrzędnych pól oraz ich współrzędnych liczbowych (tabelarycznych)
														# na wykrytej szachownicy
		self.lokalizacja= 'x9' #nieużywane z racji na złe działanie kodu
	def przypisanie_pól(self, dół, góra, x, y, w, h): #funkcja wykonuje działania mające na celu odpowiednie przypisanie współrzędnych pól

		if (góra.mean()>dół.mean()):#jeśli góra jest biała

			skok_pionowy = h / 8
			skok_poziomy = w / 8

			x = x + (skok_poziomy / 2)
			y = y + (skok_pionowy / 2)
			schowek_x = x
			kolumny = 'hgfedcba'
			for i in range(len(kolumny)):
				for j in range(1, 9):
					klucz = kolumny[i] + str(j)
					self.współrzędne.update({klucz: [x, y]})
					x = x + skok_poziomy
				x = schowek_x
				y = y + skok_pionowy

		else: #jeśli dół jest biały
			skok_pionowy = h / 8
			skok_poziomy = w / 8

			x = x + (skok_poziomy / 2)
			y = y + (skok_pionowy / 2)
			schowek_x = x
			kolumny = 'abcdefgh'
			for i in range(len(kolumny)):
				for j in range(1, 9):
					klucz = kolumny[i] + str(9-j)

					self.współrzędne.update({klucz: [x, y]})
					x = x + skok_poziomy

				x = schowek_x
				y = y + skok_pionowy ##
	def skalowanie_ekranu(self, obraz, wsp): #przeskalowanie ekranu do rozmiarów stałych, niepozwalających na błędną interpretację danych liczbowych
		wysokość = int(obraz.shape[0] * wsp)
		szerokość = int(obraz.shape[1] * wsp)
		interpolacja_ekranu = cv2.INTER_AREA


		return cv2.resize(obraz, (szerokość, wysokość), interpolacja_ekranu)
	def obrót_szachownicy(self, thresh, x,y,w,h):# funkcja określa strony tj. czy białe znajdują się na górze, czy na dole

		h=h/4
		góra=np.mean(thresh[y:y+int(h),x:x+w],(0,1))
		dół=np.mean(thresh[y+int(3*h):int(y+h*4),x:x+w],(0,1))
		#print(góra,'    ', dół)
		#print(góra.mean())
		#print(dół.mean())
		h=4*h
		self.przypisanie_pól( dół, góra, x, y, w, h)

		return
	def wstaw_bierkę(self, nazwa_bierki, x, y, w, h,  kolor, obraz, kolor_bierki):  # funkcja opisująca bierkę na podglądzie kończowym

		cv2.rectangle(obraz, (x, y), (x + w, y + h), kolor, 1)
		kolumny='abcdefgh'
		for i in range(len(kolumny)):  #niedziałający fragment kodu, mający na celu rzeczywiste
										# w czasie rozpoznawanie pola na którym stoi dana bierka
			for j in range(1, 9):
				klucz=kolumny[i]+str(j)
				wsp=self.współrzędne[klucz]
				#print(klucz)

				#if(wsp[1]<(x+w) and wsp[1] >(x) and wsp[0]<(x+w)  and wsp[0]>(y)):

		cv2.putText(obraz, kolor_bierki + " " + nazwa_bierki, (x, y),cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
	def rozpoznanie_bierki(self, kontury, obraz, thresh): #rozpoznawanie figur szachowych

		for kontur in kontury:  #znalezienie konturu szachownicy
			if (cv2.arcLength(kontur, True) > 800):
				x, y, w, h = cv2.boundingRect(kontur)
				cv2.putText(obraz, "Szachownica", (x+w+20, y + h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 200, 255), 2)


			if (cv2.arcLength(kontur, True) < 150 or cv2.arcLength(kontur, True) > 300): #pominięcie zbyt małych konturów
				continue
			kolor_bierki = "B"
			approx = cv2.approxPolyDP(kontur, 0.03 * cv2.arcLength(kontur, True),True)
			area = cv2.contourArea(kontur)    # powierzchnia bierki
			x, y, w, h = cv2.boundingRect(approx)
			rect_area = w * h #powierzchnia wykreślonego prostokąta
			s_pola = float(area) / rect_area  # stosunek pola powierzchni rect i konturu
			s_wymiarów = float(w) / h         # stosunek wymiarów szerokość długość

			kolor_pola = np.array(cv2.mean(thresh[y:y + h, x:x + w])) #okreslenie koloru bierki

			if ((area<2000)&(s_pola>0.7)&(s_wymiarów<0.8)): #rozpoznanie pionka
				kolor_ramki = (255, 255, 255)
				if kolor_pola[0] > 65:
					kolor_bierki='Cz'
					kolor_ramki = (0, 0, 0)
				self.wstaw_bierkę("Pionek", x, y, w, h,  kolor_ramki, obraz, kolor_bierki)

			if ((2700<area and area<2800)&(s_pola<0.8)&(s_wymiarów>0.9)): #Rozpoznanie Skoczka
				kolor_ramki= (255, 255, 255)
				if kolor_pola[0] > 100:
					kolor_bierki='Cz'
					kolor_ramki=(0,0,0)

				self.wstaw_bierkę("Skoczek", x, y, w, h,  kolor_ramki, obraz, kolor_bierki)

			if ((2020<area and area<2150)&(s_pola<0.65)&(s_wymiarów>0.91)): #Rozpoznanie gońca
				kolor_ramki = (255, 255, 255)
				# print('kolor - ', colors)
				# print('powierzchnia - ', area)
				# print('stosunek powierzchni - ', s_pola)
				# print('stosunek wymiarów - ', s_wymiarów)
				# print('długość konturu', float(cv2.arcLength(kontur, True)))
				if kolor_pola[0] > 74.5: #gdzieś tutuaj jest granica, ciężko złabac dla białego gońca na czarnym
					kolor_bierki='Cz'
					kolor_ramki = (0, 0, 0)
				self.wstaw_bierkę("Goniec", x, y, w, h,  kolor_ramki, obraz, kolor_bierki)

			if ((2200<area and area<2320)&(s_pola>0.78 and s_pola<0.84)&(s_wymiarów<0.9)): #Rozpozanie wieży
				kolor_ramki = (255, 255, 255)
				if kolor_pola[0] > 90:
					kolor_bierki='Cz'
					kolor_ramki = (0, 0, 0)

				self.wstaw_bierkę("Wieza", x, y, w, h, kolor_ramki, obraz, kolor_bierki)

			if ((2780<area and area<3000)&(s_pola>0.79)&(s_wymiarów>0.99)): #Rozpoznanie hetmana
				kolor_ramki = (255, 255, 255)
				if kolor_pola[0] > 106.3: #105,88 jak biały hetman stoi na czarnym polu
					kolor_bierki='Cz'
					kolor_ramki = (0, 0, 0)
				self.wstaw_bierkę("Hetman", x, y, w, h, kolor_ramki, obraz, kolor_bierki)

			if ((2300<area and area<2450)&(s_pola<0.75)&(s_wymiarów>0.93)): #Rozpoznanie króla
				kolor_ramki=(255, 255, 255)
				if kolor_pola[0] > 78: #77,5 jak biały król stoi na czarnym polu
					kolor_bierki='Cz'
					kolor_ramki= (0, 0, 0)

				self.wstaw_bierkę("Krol", x, y, w, h,  kolor_ramki, obraz, kolor_bierki)

		cv2.imshow('Przebieg partii', obraz)
	def start(self):
		cap = cv2.VideoCapture('nagrania/Chess.com.mkv')

		ret, obraz = cap.read() #Zebranie kratki do określenia wymiarów szachownicy
		if ret: #obróbka orbazu
			obraz = self.skalowanie_ekranu(obraz, 0.6)
			gray = cv2.cvtColor(obraz, cv2.COLOR_BGR2GRAY)
			thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 3)
			_, threshold_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
			morfo = cv2.morphologyEx(threshold_otsu, cv2.MORPH_ERODE, np.ones((7, 7), np.uint8))
			kontury, hierarchia = cv2.findContours(morfo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

			for kontur in kontury:
				if (cv2.arcLength(kontur, True) > 900):
					x, y, w, h = cv2.boundingRect(kontur)
					#cv2.rectangle(obraz, (x, y), (x + w, y + h), (255,0,0), 5)
					#cv2.imshow('o',obraz)

					self.obrót_szachownicy(obraz, x, y, w, h)

		while (True):#pętla programu

			ret, obraz = cap.read()
			if ret:
				obraz = self.skalowanie_ekranu(obraz, 0.6)
				gray = cv2.cvtColor(obraz, cv2.COLOR_BGR2GRAY)
				thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 3)
				_, threshold_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
				morfo = cv2.morphologyEx(threshold_otsu, cv2.MORPH_ERODE, np.ones((7,7), np.uint8))
				kontury, hierarchia = cv2.findContours(morfo, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)


				self.rozpoznanie_bierki(kontury, obraz.copy(), thresh.copy())

				if cv2.waitKey(1) and 0xFF == ord('q'):
					break
			else:
				break
	cv2.destroyAllWindows()

program = Szachy()
program.start()
